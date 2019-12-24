from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gevent
import socket
import sys
from datetime import date
import time
import stream_readwriter
import threading

import message


def subscribe_handler(body):
    print('SUBSCRIBE', threading.get_ident())


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

#stream_readwriter.subscribe_stock(sock, 'A005930')
message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()
#stream_readwriter.subscribe_stock(message_reader, 'A005930', subscribe_handler)
while True:
    #stream_readwriter.request_stock_day_data(sock, 'A005930', date(2019, 12, 20), date(2019, 12, 20)) 
    print('send threading', threading.get_ident())
    print(stream_readwriter.request_stock_day_data(message_reader, 'A005930', date(2019, 12, 24), date(2019, 12, 24)))
    print('send done', threading.get_ident())
    time.sleep(10)
