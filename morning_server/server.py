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

import message
from morning.config import db
from morning_server.handlers import request_pre_handler as request_pre_handler
import server_util
from server_util import stream_write


VBOX_CHECK_INTERVAL = 60 # 1 minute

app = Flask(__name__)
app.debug = True
vbox_on = False
collectors = server_util.CollectorList()
subscribe_client = server_util.SubscribeClient()
partial_request = server_util.PartialRequest()


def handle_collector(sock, header, body):
    print('HANDLE COLLECTOR', hex(threading.get_ident()))
    collectors.add_collector(sock, body)


def handle_response(sock, header, body):
    print('HANDLE RESPONSE', header)
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
    print('HANDLE RESPONSE DONE')



def handle_request(sock, header, body):
    print('HANDLE REQUEST', header)
    data, vacancy = request_pre_handler.pre_handle_request(sock, header, body)
    if data is None:
        collector = collectors.get_available_request_collector()
        collector.set_request(sock, header['_id'], True)
        stream_write(collector.sock, header, body, collectors)
    elif len(vacancy) > 0:
        partial_request.start_partial_request(header, data, len(vacancy))
        for v in vacancy:
            collector = collectors.get_available_request_collector()
            # TODO: create separate header ID
            collector.set_request(sock, header['_id'], True)
            header['from'] = v[0]
            header['until'] = v[1]
            stream_write(collector.sock, header, body, collectors)
    else:
        header['type'] = message.RESPONSE
        stream_write(sock, header, data)
    print('HANDLE REQUEST DONE')


def handle_subscribe(sock, header, body):
    #print('HANDLE SUBSCRIBE', hex(threading.get_ident()))
    code = header['code']
    subscribe_client.add_to_clients(code, sock, header, body, collectors)


def handle_subscribe_response(sock, header, body):
    #print('HANDLE SUBSCRIBE RESPONSE', hex(threading.get_ident()))
    code = header['code']
    subscribe_client.send_to_clients(code, header, body)


def handle_trade_response(sock, header, body):
    pass


def handle_trade_request(sock, header, body):
    pass


def handle(sock, address):
    print('new connection', hex(threading.get_ident()))
    print('address', address)
    try:
        stream_readwriter.dispatch_message(sock, collector_handler=handle_collector, 
                                            request_handler=handle_request,
                                            response_handler=handle_response, 
                                            subscribe_handler=handle_subscribe,
                                            subscribe_response_handler=handle_subscribe_response, 
                                            request_trade_handler=handle_trade_request,
                                            response_trade_handler=handle_trade_response)
    except Exception as e:
        print('Dispatch exception', e)
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
            vbox_controller.start_machine()
            vbox_on = False
        elif not vbox_on and not is_turn_off_time:
            vbox_on = True
            vbox_controller.stop_machine()

        gevent.sleep(VBOX_CHECK_INTERVAL)



server = StreamServer((message.SERVER_IP, message.CLIENT_SOCKET_PORT), handle)
server.start()

#gevent.Greenlet.spawn(vbox_control)

wsgi_server = pywsgi.WSGIServer((message.SERVER_IP, message.CLIENT_WEB_PORT), app)
wsgi_server.serve_forever()
