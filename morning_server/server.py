from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from flask import Flask
from gevent import pywsgi
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


VBOX_CHECK_INTERVAL = 60 # 1 minute

app = Flask(__name__)
app.debug = True
vbox_on = False
collectors = server_util.CollectorList()
subscribe_client = server_util.SubscribeClient()
partial_request = server_util.PartialRequest()


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
    if header['vendor'] == message.CYBOS:
        handle_request_cybos(sock, header, body)
    elif header['vendor'] == message.KIWOOM:
        handle_request_kiwoom(sock, header, body)

    logger.info('HANDLE REQUEST DONE')


def handle_subscribe(sock, header, body):
    logger.info('HANDLE SUBSCRIBE %s', hex(threading.get_ident()))
    code = header['code']
    stop_methods = [message.STOP_ALARM_DATA]
    if header['method'] in stop_methods:
        subscribe_client.remove_from_clients(code, sock, header, body, collectors)
    else:
        subscribe_client.add_to_clients(code, sock, header, body, collectors)


def handle_subscribe_response(sock, header, body):
    logger.info('HANDLE SUBSCRIBE RESPONSE %s', hex(threading.get_ident()))
    code = header['code']
    subscribe_client.send_to_clients(code, header, body)
    logger.info('HANDLE SUBSCRIBE RESPONSE DONE')


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
            stream_write(collector.sock, header, body, collectors)

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
        

@app.route('/')
def index():
    return 'hello world'


def vbox_control():
    global vbox_on
    import trade_machine
    vbox_controller = trade_machine.VBoxControl()
    while True:
        now = datetime.now()
        year, month, day = now.year, now.month, now.day
        is_turn_off_time = datetime(year, month, day, 5) <= now <= datetime(year, month, day, 7)
        if vbox_on and is_turn_off_time:
            vbox_controller.stop_machine()
            #TODO: reset collectors
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

wsgi_server = pywsgi.WSGIServer((message.SERVER_IP, message.CLIENT_WEB_PORT), app)
wsgi_server.serve_forever()

log_server.join()
