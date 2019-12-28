from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gevent
import socket
import sys
from datetime import date
import time
import threading

from morning_server import stock_api
from morning_server import message
from morning_server import stream_readwriter


def subscribe_handler(code, body):
    print('SUBSCRIBE', threading.get_ident())
    print(body)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()
stock_api.subscribe_stock(message_reader, 'A005930', subscribe_handler)
while True:
    #stream_readwriter.request_stock_day_data(sock, 'A005930', date(2019, 12, 20), date(2019, 12, 20)) 
    print('send threading', threading.get_ident())
    print('LEN', len(stock_api.request_stock_minute_data(message_reader, 'A005930', date(2019, 12, 2), date(2019, 12, 2))))
    print('send done', threading.get_ident())
    gevent.sleep(5)
