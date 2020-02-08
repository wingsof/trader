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
from clients.snake import today_watcher, trade_account, trader_env


window_size = 5


def get_window_data(reader, code, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, until_date - timedelta(days=int(window_size*2)), until_date)
    if window_size > len(past_data):
        return []
    elif past_data[-1]['0'] != time_converter.datetime_to_intdate(until_date):
        return []

    past_data_c = []
    for data in past_data[-window_size:]:
        past_data_c.append(dt.cybos_stock_day_tick_convert(data))

    return past_data_c


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    search_from = date(2019, 1, 2)
    search_until = date(2019, 1, 30)

    result = []
    while search_from <= search_until:
        if holidays.is_holidays(search_from):
            search_from += timedelta(days=1)
            continue

        for progress, code in enumerate(market_code):
            print(search_from, f'{progress+1}/{len(market_code)}', end='\r')
            past_data = get_window_data(message_reader, code, search_from)
            if len(past_data) == 0:
                continue
            last_close = past_data[window_size-1]['close_price']
            first_close = past_data[0]['close_price']

            min_price = min([d['lowest_price'] for d in past_data])
            max_price = max([d['highest_price'] for d in past_data])
            profit = (last_close - first_close) / first_close * 100
            average_amount = np.array([d['amount'] for d in past_data]).mean()
            risk = (max_price - min_price) / min_price * 100

            if profit >= 10 or profit <= -10:
                result.append({'code': code, 'profit': profit, 'risk': risk, 'date': search_from, 'average_amount': average_amount})
        print('')
        search_from += timedelta(days=1)
    df = pd.DataFrame(result)
    df.to_excel('ten_within_week.xlsx')
