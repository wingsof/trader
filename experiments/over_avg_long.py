from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
import time
import threading
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db

TEST_MODE = False

def rprint(*kargs, **kwargs):
    if not TEST_MODE:
        print(*kargs, **kwargs)


def mprint(*kargs):
    if TEST_MODE:
        print(*kargs)


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    avg_volumes = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        avg_volumes = np.append(avg_volumes, np.array([converted['volume']]))

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
            converted['volume_average'] = avg_volumes.mean()
            avg_volumes = avg_volumes[1:]
        else:
            converted['moving_average'] = 0
            converted['avg_volumes'] = 0

        converted_data.append(converted)

    return converted_data


def get_today_min_data(code, from_date):
    today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
    if len(today_min_data) == 0:
        print('NO MIN DATA', code, from_date)
        return []
    today_min_data_c = []
    for tm in today_min_data:
        today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))
    return today_min_data_c


def start_trade(min_data, yesterday_close):
    start_price = min_data[0]['start_price']
    start_trace = False
    # Try: from start price and react when +-9%
    for j, tm in enumerate(min_data):
        current_profit = (tm['close_price'] - start_price) / start_price * 100.
        today_profit = (tm['close_price'] - yesterday_close) / yesterday_close * 100.
        #if code == 'A018620':
        #    print(code, abs(current_profit))
        if start_trace:
            if j == len(min_data) - 1:
                #print(code, dates[i], 'SELL at the end', current_profit)
                return start_price, tm['close_price'], today_profit
            else:
                if (tm['close_price'] - tm['highest_price']) / tm['highest_price'] * 100. < -4.:
                    #print(code, dates[i], 'SELL', current_profit)
                    return start_price, tm['close_price'], today_profit
        elif j == len(min_data) - 1:
            if today_profit > 25:
                #print(code, dates[i], 'SELL at the end(no trace)', current_profit)
                return start_price, tm['close_price'], today_profit
            else:
                pass
                #print('NOT SELL', code, dates[i])
        elif abs(current_profit) > 9.:
            start_trace = True
    return 0, 0, 0


if __name__ == '__main__':
    MAVG=20

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)

    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()


    if TEST_MODE:
        market_code = ['A035620']
        dates = []
        no_buy_indexes = []
        #market_code = ['A099410', 'A061040', 'A047310', 'A053660', 'A027050', 'A089970', 'A032685', 'A010240', 'A017890', 'A168330', 'A048470']
    else:
        market_code = ['A018620', 'A087730', 'A054630', 
                        'A073560', 'A100590', 'A066130',
                        'A042510', 'A079960', 'A215100',
                        'A170790', 'A148140', 'A052900',
                        'A290550', 'A000440', 'A000440', 
                        'A053280', 'A215090']
        dates = [
            date(2019, 9, 18), date(2019, 12, 24), date(2019, 4, 25),
            date(2019, 3, 12), date(2019, 9, 4), date(2019, 1, 24),
            date(2019, 2, 21), date(2019, 11, 15), date(2019, 3, 11),
            date(2019, 11, 13), date(2019, 1, 24), date(2019, 7, 4),
            date(2019, 9, 6), date(2019, 9, 16), date(2019, 9, 17),
            date(2019, 5, 15), date(2019, 8,27)
        ]

        no_buy_indexes = [13]

    code_dict = dict()

    # Ignore close price under mavg here
    profit_average = []
    for i, code in enumerate(market_code):
        yesterday = holidays.get_yesterday(dates[i])
        min_data = get_today_min_data(code, dates[i])
        if len(min_data) == 0:
            print('NO DATA', code)
            continue
        yesterday_data = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        if len(yesterday_data) == 0:
            print('NO DAY DATA', code)
            continue
        yesterday_data = yesterday_data[0]
        open_price, close_price, profit = start_trade(min_data, yesterday_data['5'])
        if open_price != 0:
            profit_average.append(profit)


    if not TEST_MODE:
        print('PROFITS', profit_average)
        print('MEAN', np.array(profit_average).mean())
        print('STD', np.array(profit_average).std())
