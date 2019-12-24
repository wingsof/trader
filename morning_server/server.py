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

import message
from morning.config import db


app = Flask(__name__)
collectors = []


def datetime_to_intdate(dt):
    return dt.year * 10000 + dt.month * 100 + dt.day


def handle_collector(sock, header, body):
    print('HANDLE COLLECTOR', hex(threading.get_ident()))
    collectors.append({
        'socket': sock,
        'capability': body['capability'],
        'subscribe_count': 0,
        'request_pending': False
    })


def handle_request(sock, header, body):
    print('HANDLE REQUEST', hex(threading.get_ident()))
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


def handle(sock, address):
    print('new connection', hex(threading.get_ident()))
    print('address', address)
    stream_readwriter.dispatch_message(sock, handle_collector, handle_request, handle_subscribe)
    

@app.route('/')
def index():
    return 'hello world'


server = StreamServer(('127.0.0.1', 27019), handle)
server.start()
wsgi_server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
wsgi_server.serve_forever()
