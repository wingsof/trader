from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from gevent.server import StreamServer
from datetime import datetime
import threading
import stream_readwriter
import time
import gevent
import virtualbox
from multiprocessing import Process

import message
from morning.config import db
from morning_server.handlers import request_pre_handler as request_pre_handler
import server_util
from server_util import stream_write
from utils import logger_server, logger
from morning_server import morning_stats


VBOX_CHECK_INTERVAL = 60 # 1 minute

vbox_on = False
collectors = server_util.CollectorList()
subscribe_client = server_util.SubscribeClient()
partial_request = server_util.PartialRequest()
morning_stat = morning_stats.MorningStats(collectors)


def handle_collector(sock, header, body):
    logger.info('HANDLE COLLECTOR %s', hex(threading.get_ident()))
    collectors.add_collector(sock, header, body)


def handle_response(sock, header, body):
    logger.info('HANDLE RESPONSE %s', header)
    item = partial_request.get_item(header['_id'])
    collector = collectors.find_by_id(header['_id'])

    if item is not None:
        if item.add_body(body, header): # Message completed
            data = item.get_whole_message()
            stream_write(collector.request_socket(), header, data, subscribe_client)
            partial_request.pop_item(header['_id'])
    else:
        stream_write(collector.request_socket(), header, body, subscribe_client)

    collector.set_pending(False)
    logger.info('HANDLE RESPONSE DONE')


def handle_request_cybos(sock, header, body):
    data, vacancy = request_pre_handler.pre_handle_request(sock, header, body)
    if data is None:
        logger.info('HEADER ' +str(header))
        collector = collectors.get_available_request_collector()
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, collectors)
    elif len(vacancy) > 0:
        logger.info('HEADER(to collector) ' + str(header))
        partial_request.start_partial_request(header, data, len(vacancy))
        for v in vacancy:
            collector = collectors.get_available_request_collector()
            # TODO: create separate header ID
            collector.set_request(sock, header['_id'], True)
            header['from'] = v[0]
            header['until'] = v[1]
            stream_write(collector.sock, header, body, collectors)
    else:
        logger.info('HEADER(cached) %s', header)
        header['type'] = message.RESPONSE
        stream_write(sock, header, data)


def handle_request_kiwoom(sock, header, body):
    collector = collectors.get_available_request_collector(message.KIWOOM)
    collector.set_request(sock, header['_id'], True)
    stream_write(collector.sock, header, body, collectors)


def handle_request(sock, header, body):
    logger.info('HANDLE REQUEST %s', header)
    if header['method'] == message.SUBSCRIBE_STATS:
        header['type'] = message.RESPONSE
        stream_write(sock, header, morning_stat.get_subscribe_response_info())
    elif header['method'] == message.COLLECTOR_STATS:
        header['type'] = message.RESPONSE
        stream_write(sock, header, morning_stat.get_collector_info())
    elif header['vendor'] == message.CYBOS:
        handle_request_cybos(sock, header, body)
    elif header['vendor'] == message.KIWOOM:
        handle_request_kiwoom(sock, header, body)

    logger.info('HANDLE REQUEST DONE')


def handle_subscribe(sock, header, body):
    logger.info('HANDLE SUBSCRIBE %s', hex(threading.get_ident()))
    code = header['code']
    stop_methods = [message.STOP_ALARM_DATA,
                    message.STOP_STOCK_DATA,
                    message.STOP_BIDASK_DATA,
                    message.STOP_WORLD_DATA,
                    message.STOP_INDEX_DATA,
                    message.STOP_SUBJECT_DATA]
    if header['method'] in stop_methods:
        subscribe_client.remove_from_clients(code, sock, header, body, collectors)
    else:
        subscribe_client.add_to_clients(code, sock, header, body, collectors)


def handle_subscribe_response(sock, header, body):
    #logger.info('HANDLE SUBSCRIBE RESPONSE %s', hex(threading.get_ident()))
    code = header['code']
    subscribe_client.send_to_clients(code, header, body)
    morning_stat.increment_subscribe_count(code)
    #logger.info('HANDLE SUBSCRIBE RESPONSE DONE')


def handle_trade_response(sock, header, body):
    logger.info('HANDLE TRADE RESPONSE %s', header)
    collector = collectors.find_by_id(header['_id'])
    stream_write(collector.request_socket(), header, body, subscribe_client)
    collector.set_pending(False)


def handle_trade_request(sock, header, body):
    logger.info('HANDLE TRADE REQUEST %s', header)
    collector = collectors.get_available_trade_collector()
    if header['method'] == message.TRADE_DATA:
        subscribe_client.add_trade_to_clients(sock, collector.sock)
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, collectors)
    elif header['method'] == message.STOP_TRADE_DATA:
        subscribe_client.remove_trade_from_clients(sock)
        if subscribe_client.count_of_trade_client() == 0:
            # send to collector
            stream_write(collector.sock, header, body, collectors)

        # send to client
        header['type'] = message.RESPONSE_TRADE
        body = {'result': True}
        stream_write(sock, header, body, collectors)
    else:
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, collectors)


def handle_trade_subscribe_response(sock, header, body):
    logger.info('HANDLE TRADE SUBSCRIBE RESPONSE %s', header)
    subscribe_client.send_trade_to_client(header, body)


def handle(sock, address):
    logger.info('new connection, address ' + str(address))
    try:
        stream_readwriter.dispatch_message(sock, collector_handler=handle_collector, 
                                            request_handler=handle_request,
                                            response_handler=handle_response, 
                                            subscribe_handler=handle_subscribe,
                                            subscribe_response_handler=handle_subscribe_response, 
                                            request_trade_handler=handle_trade_request,
                                            response_trade_handler=handle_trade_response,
                                            subscribe_trade_response_handler=handle_trade_subscribe_response)
    except Exception as e:
        logger.warning('Dispatch exception ' + str(e))
        collectors.handle_disconnect(e.args[1])
        subscribe_client.handle_disconnect(e.args[1])
        

def send_shutdown_msg():
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.SHUTDOWN)
    body = []
    for c in collectors.collectors:
        stream_write(c.sock, header, body)


def vbox_control():
    global vbox_on
    global collectors
    global subscribe_client
    global partial_request
    import trade_machine
    vbox_controller = trade_machine.VBoxControl()
    while True:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        is_turn_off_time = datetime(year, month, day, 5) <= now <= datetime(year, month, day, 6, 30)
        if vbox_on and is_turn_off_time:
            send_shutdown_msg()
            collectors.reset()
            subscribe_client.reset()
            partial_request.reset()
            vbox_controller.stop_machine()
            vbox_on = False
        elif not vbox_on and not is_turn_off_time:
            vbox_on = True
            vbox_controller.start_machine()

        gevent.sleep(VBOX_CHECK_INTERVAL)


log_server = Process(target=logger_server.start_log_server)
log_server.start()

server = StreamServer((message.SERVER_IP, message.CLIENT_SOCKET_PORT), handle)
server.start()

if len(sys.argv) > 1 and sys.argv[1] == 'vbox':
    gevent.Greenlet.spawn(vbox_control)

log_server.join()
