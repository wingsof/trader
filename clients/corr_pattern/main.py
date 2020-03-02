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
from configs import db
from clients.snake import today_watcher, trade_account, trader_env


window_size = 90
future_day = 10


def get_future_data(reader, code, from_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, from_date + timedelta(days=int(future_day*2)))
    if len(past_data) < future_day:
        return []
    past_data_c = []
    for data in past_data[:future_day+1]:
        past_data_c.append(dt.cybos_stock_day_tick_convert(data))
    start_price = past_data_c[0]['close_price'] 
    profits = []
    for data in past_data_c[1:]:
        profits.append((data['close_price'] - start_price) / start_price * 100)
    return profits


def get_window_data(reader, code, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, until_date - timedelta(days=int(window_size*2)), until_date)
    if window_size > len(past_data):
        return [], [], [], [], []
    elif past_data[-1]['0'] != time_converter.datetime_to_intdate(until_date):
        return [], [], [], [], []

    past_data_c = []
    for data in past_data[-90:]:
        past_data_c.append(dt.cybos_stock_day_tick_convert(data))

    close_datas = [d['close_price'] for d in past_data_c]
    amount_datas = [d['amount'] for d in past_data_c]

    close_datas_recent = close_datas[-30:]
    amount_datas_recent = amount_datas[-30:]

    return past_data_c, close_datas, amount_datas, close_datas_recent, amount_datas_recent

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    target_code = ['A034230']
    search_from = date(2019, 1, 2)
    search_until = date(2019, 12, 30)

    for code in target_code:
        today = datetime.now().date()
        yesterday = holidays.get_yesterday(today)
        yesterday = holidays.get_yesterday(yesterday)
        past_data, prices, amounts, recent_prices, recent_amounts = get_window_data(message_reader, code, yesterday)
        average_amount = np.array(recent_amounts).mean()

        while search_from <= search_until:
            if holidays.is_holidays(search_from):
                search_from += timedelta(days=1)
                continue
            for mcode in market_code:
                mpast_data, mprices, mamounts, recent_mprices, recent_mamounts = get_window_data(message_reader, mcode, search_from)
                if len(mpast_data) == 0:
                    continue
                recent_amount_average = np.array(recent_mamounts).mean()
                if (average_amount * 0.7 >  recent_amount_average or
                            average_amount * 1.3 < recent_amount_average):
                    continue

                recent_price_corr = scipy.stats.pearsonr(np.array(recent_prices), np.array(recent_mprices))
                recent_amounts_corr = scipy.stats.pearsonr(np.array(recent_amounts), np.array(recent_mamounts))
                if recent_price_corr[0] >= 0.5 and recent_amounts_corr[0] >= 0.5:
                    price_corr = scipy.stats.pearsonr(np.array(prices), np.array(mprices))
                    amounts_corr = scipy.stats.pearsonr(np.array(amounts), np.array(mamounts))
                    if price_corr[0] >= 0.5:
                        print(mcode, search_from, 
                                    float("{0:.2f}".format(recent_price_corr[0])),
                                    float("{0:.2f}".format(recent_amounts_corr[0])),
                                    float("{0:.2f}".format(price_corr[0])),
                                    float("{0:.2f}".format(amounts_corr[0])))
                        profits = get_future_data(message_reader, mcode, search_from)
                        for p in profits:
                            print(float("{0:.2f}".format(p)), end=' ')
                        print('')
            search_from += timedelta(days=1)

""" result
A192440 2019-04-18 0.71 0.74 0.7 0.64
6.27 8.89 9.04 6.71 8.02 8.02 8.6 10.2 10.93 11.52
A218410 2019-05-21 0.81 0.52 0.8 0.61
0.18 -8.5 -19.59 -12.94 0.0 2.77 -1.85 -3.33 -5.18 -6.84
A218410 2019-05-22 0.83 0.63 0.79 0.6
-8.67 -19.74 -13.1 -0.18 2.58 -2.03 -3.51 -5.35 -7.01 -5.72
A218410 2019-05-27 0.68 0.65 0.68 0.58
14.86 18.05 12.74 11.04 8.92 7.01 8.49 12.1 19.53 21.66
A178320 2019-05-30 0.51 0.82 0.56 0.61
-1.58 -2.17 1.19 -0.2 6.72 8.7 7.91 9.29 8.7 11.26
A038540 2019-08-07 0.59 0.7 0.63 0.59
13.46 20.19 21.63 14.9 6.73 9.62 9.62 14.9 14.9 11.54
A150840 2019-11-21 0.63 0.66 0.64 0.64
-29.63 -21.92 -24.72 -28.13 -32.63 -37.64 -35.14 -39.34 -39.34 -37.54
A150840 2019-11-22 0.74 0.5 0.68 0.54
10.95 6.97 2.13 -4.27 -11.38 -7.82 -13.8 -13.8 -11.24 -13.09
A150840 2019-11-25 0.82 0.54 0.72 0.56
-3.59 -7.95 -13.72 -20.13 -16.92 -22.31 -22.31 -20.0 -21.67 -25.64
"""
