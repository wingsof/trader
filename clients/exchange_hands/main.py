from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

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

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db

MAVG=20
STATE_NONE=0
STATE_BULL=1
STATE_BUY=2

code_dict = dict()
report = []

def get_past_data(reader, code, from_date, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, until_date)
    return past_data


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


def print_code_dict(code, d):
    print('DATE', d, '\t', 'CODE', code, '\t', 'STATE', code_dict[code]['state'], '\t', 'BOUGHT PRICE', code_dict[code]['bought_price'])


def start_today_trading(reader, market_code, today):
    for code in market_code:
        data = get_past_data(reader, code, today, today)
        data =convert_data_readable(code, data)
        if len(data) != 1:
            continue

        data = data[0]
        if data['close_price'] < 900:
            continue

        state = code_dict[code]['state']
        if code_dict[code]['yesterday_close'] == 0:
            code_dict[code]['yesterday_close'] = data['close_price']
            continue

        if state == STATE_NONE:
            profit = (data['close_price'] - data['start_price']) / data['start_price'] * 100
            if profit > 6 and data['amount'] > 30000000000:
                past_data = get_past_data(reader, code, today - timedelta(days=120), holidays.get_yesterday(today))
                past_data = convert_data_readable(code, past_data)
                if len(past_data) < 70:
                    #print(today, 'short data')
                    continue
                past_data = past_data[-70:]
                recent_low = min([d['lowest_price'] for d in past_data[-10:]])
                all_low = min([d['lowest_price'] for d in past_data])
                recent_has_low = recent_low == all_low
                if recent_has_low:
                    recent_max_amount = max([d['amount'] for d in past_data[-10:]])
                    #print('recent', recent_max_amount, 'today', data['amount'], data['cum_buy_volume'], data['cum_sell_volume'])
                    if recent_max_amount * 2 < data['amount'] and data['cum_buy_volume'] > data['cum_sell_volume'] * 2:
                        code_dict[code]['state'] = STATE_BULL
                        code_dict[code]['amount'] = data['amount']
                        code_dict[code]['org_price'] = []
                        code_dict[code]['cut_price'] = (data['close_price'] - recent_low) / 3 + recent_low
                        code_dict[code]['ready'] = False
                        print_code_dict(code, today)
        elif state == STATE_BULL:
            #TODO: check exchange hands
            #print(data['lowest_price'], code_dict[code]['cut_price'])
            today_profit = (data['close_price'] - code_dict[code]['yesterday_close']) / code_dict[code]['yesterday_close'] * 100
            if code_dict[code]['ready']:
                code_dict[code]['bought_price'] = data['start_price']
                code_dict[code]['state'] = STATE_BUY
                print_code_dict(code, today)
            if data['lowest_price'] < code_dict[code]['cut_price']:
                code_dict[code]['state'] = STATE_NONE
                print_code_dict(code, today)
            elif today_profit >= 5:
                code_dict[code]['ready'] = True
        elif state == STATE_BUY:
            today_profit = (data['close_price'] - code_dict[code]['yesterday_close']) / code_dict[code]['yesterday_close'] * 100
            if code_dict[code]['bought_price'] > data['close_price']:
                profit = (data['close_price'] - code_dict[code]['bought_price']) / code_dict[code]['bought_price'] * 100
                print(code, today, 'CUT', profit)
                code_dict[code]['state'] = STATE_NONE
                print_code_dict(code, today)
            elif today_profit > 5:
                profit = (data['close_price'] - code_dict[code]['bought_price']) / code_dict[code]['bought_price'] * 100
                print(code, today, 'OK', profit)
                code_dict[code]['state'] = STATE_NONE
                print_code_dict(code, today)
        
        code_dict[code]['yesterday_close'] = data['close_price']

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    #market_code = ['A005290']

    from_date = date(2019, 6, 1)
    until_date = date(2020, 2, 10)

    for code in market_code:
        code_dict[code] = {'state': STATE_NONE,
                            'amount': 0,
                            'cut_price': 0,
                            'org_prices': [],
                            'ready': False,
                            'yesterday_close': 0,
                            'bought_price': 0}

    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        start_today_trading(message_reader, market_code, from_date)
        from_date += timedelta(days=1)
