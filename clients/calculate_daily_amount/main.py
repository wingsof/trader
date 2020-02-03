"""
    1. search past data and set status of each code
    2. get long list and set status of each code status
    3. start subscribe for selected codes
    4. Do trades according to rules
"""

from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import date, timedelta, datetime
import gevent
import socket
import scipy
import sys
import time
import threading
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db


def get_data(reader, code, d):
    past_data = stock_api.request_stock_day_data(reader, code, d, d)
    if len(past_data) != 1:
        return None

    past_data_c = []
    for data in past_data:
        past_data_c.append(dt.cybos_stock_day_tick_convert(data))

    return past_data_c[0]


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    search_from = date(2019, 1, 2)
    search_until = date(2019, 12, 30)

    result = dict()
    while search_from <= search_until:
        if holidays.is_holidays(search_from):
            search_from += timedelta(days=1)
            continue
        
        day_datas = []
        for progress, code in enumerate(market_code):
            print(search_from, f'{progress+1}/{len(market_code)}', end='\r')
            past_data = get_data(message_reader, code, search_from)
            if past_data is None:
                continue
            day_datas.append(past_data)

        print('')
        day_datas = sorted(day_datas, key=lambda x: x['amount'], reverse=True)
        for i in range(20, (300 if len(day_datas) > 300 else len(day_datas)), 20):
            amount_mean = np.array([d['amount'] for d in day_datas[i-20:i]]).mean()
            if i in result:
                result[i].append(amount_mean)
            else:
                result[i] = [amount_mean]
        
        search_from += timedelta(days=1)
    report = []
    for k, v in result.items():
        arr = np.array(v)
        report.append({'up_to': k, 'mean': arr.mean(), 'std': arr.std()}) 
    df = pd.DataFrame(report)
    df.to_excel('amount_report.xlsx')
