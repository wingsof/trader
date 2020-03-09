"""
    1. Check delays when subscirbe 800 codes
"""

from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import date, timedelta, datetime, time
import gevent
import socket
import sys
import threading
import pandas as pd
import numpy as np
from pymongo import MongoClient

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from configs import db


within_time_count = 0
out_time_count = 0

def handler(code, datas):
    global within_time_count
    global out_time_count
    tick_data = []
    now = datetime.now()
    for d in datas:
        tick_data.append(dt.cybos_stock_tick_convert(d))
    if len(tick_data) == 0:
        return
    elif len(tick_data) > 1:
        print('tick data len is over 1')
        
    data = tick_data[0]
    hour = int(data['time_with_sec'] / 10000)
    min = int(data['time_with_sec'] % 10000 / 100)
    second = int(data['time_with_sec'] % 100)
    data['date'] = datetime.combine(now.date(), time(hour, min, second))
    if now - data['date'] > timedelta(seconds=30):
        print('delayed', (now - data['date']).seconds)
        out_time_count += 1
    else:
        within_time_count += 1

def count_check():
    while True:
        print('within', within_time_count, 'out', out_time_count)
        gevent.sleep(5)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    print('request code done')
    market_code = market_code[:200]
    gevent.spawn(count_check)

    for code in market_code:
        print('request subscribe', code)
        stock_api.subscribe_stock(message_reader, code, handler)
    print('waiting data')
    message_reader.join()
