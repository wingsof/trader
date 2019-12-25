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


app = Flask(__name__)
app.debug = True
VBOX_CHECK_INTERVAL = 60 # 1 minute
collectors = []
subscribe_clients = dict()


def datetime_to_intdate(dt):
    return dt.year * 10000 + dt.month * 100 + dt.day


def find_request_collector():
    for c in collectors:
        if c['capability'] | message.CAPABILITY_REQUEST_RESPONSE and not c['request_pending']:
            return c
    return None


def find_collector_by_id(msg_id):
    for c in collectors:
        if c['request_id'] == msg_id:
            return c
    return None


def handle_collector(sock, header, body):
    print('HANDLE COLLECTOR', hex(threading.get_ident()))
    collectors.append({
        'socket': sock,
        'capability': body['capability'],
        'subscribe_count': 0,
        'request_pending': False,
        'request_id': None,
        'request_socket': None
    })


def handle_response(sock, header, body):
    collector = find_collector_by_id(header['_id'])
    collector['request_pending'] = False
    stream_readwriter.write(collector['request_socket'], header, body)


def handle_request(sock, header, body):
    print('HANDLE REQUEST', hex(threading.get_ident()))
    collector = None
    while True:
        collector = find_request_collector()
        if collector is not None:
            break

    collector['request_socket'] = sock
    collector['request_id'] = header['_id']
    stream_readwriter.write(collector['socket'], header, body)
    
    """

    stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    code = body['code']
    from_datetime = body['from']
    until_datetime = body['until']
    data = list(stock_db[code + '_D'].find({'0': {
        '$gte': datetime_to_intdate(from_datetime),
        '$lte': datetime_to_intdate(until_datetime)}}))
    header['type'] = message.RESPONSE
    time.sleep(5)
    
    stream_readwriter.write(sock, header, data)
    """
    print('HANDLE REQUEST DONE', hex(threading.get_ident()))


def deliver_stream(code, sock, header):
    # First find whether code is already subscribing
    # Otherwise find subscibe server to start new stream
    stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    data = list(stock_db[code].find({'date': {
        '$gte': datetime(2019, 12, 23),
        '$lte': datetime(2019, 12, 24)}}))

    for d in data:
        stream_readwriter.write(sock, header, d)
        time.sleep(1)


def handle_subscribe(sock, header, body):
    print('HANDLE SUBSCRIBE', hex(threading.get_ident()))
    code = body['code']
    gevent.spawn(deliver_stream, code, sock, header)


def handle_subscribe_response(sock, header, body):
    pass

def handle_trade_response(sock, header, body):
    pass


def handle_trade_request(sock, header, body):
    pass


def handle(sock, address):
    print('new connection', hex(threading.get_ident()))
    print('address', address)
    stream_readwriter.dispatch_message(sock, collector_handler=handle_collector, request_handler=handle_request, response_handler=handle_response, 
                                        subscribe_handler=handle_subscribe, subscribe_response_handler=handle_subscribe_response, 
                                        request_trade_handler=handle_trade_request, response_trade_handler=handle_trade_response)
    

@app.route('/')
def index():
    return 'hello world'


def vbox_control():
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


vbox_on = False

server = StreamServer((message.SERVER_IP, message.CLIENT_SOCKET_PORT), handle)
server.start()

gevent.Greenlet.spawn(vbox_control)

wsgi_server = pywsgi.WSGIServer((message.SERVER_IP, 5000), message.CLIENT_WEB_PORT)
wsgi_server.serve_forever()
