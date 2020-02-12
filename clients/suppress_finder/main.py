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
    yesterday_close = 0
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        if yesterday_close == 0:
            yesterday_close = converted['close_price']
            continue
        converted['code'] = code
        converted['yesterday_close'] = yesterday_close
        converted_data.append(converted)
        yesterday_close = converted['close_price']

    return converted_data


def print_code_dict(code, d):
    print('DATE', d, '\t', 'CODE', code, '\t', 'STATE', code_dict[code]['state'])


def start_today_trading(reader, market_code, today):
    for code in market_code:
        data = get_past_data(reader, code, holidays.get_yesterday(today), today)
        data = convert_data_readable(code, data)
        if len(data) != 1:
            #print('no data')
            continue

        data = data[0]
        state = code_dict[code]['state']

        if state == STATE_NONE:
            profit = (data['close_price'] - data['start_price']) / data['start_price'] * 100
            if profit > 10:
                past_data = get_past_data(reader, code, today - timedelta(days=12), holidays.get_yesterday(today))
                past_data = convert_data_readable(code, past_data)
                if len(past_data) < 5:
                    print(today, 'short data')
                    continue
                past_data = past_data[-5:]
                past_profits = [abs((d['close_price'] - d['yesterday_close']) / d['yesterday_close'] * 100) <= 3. for d in past_data]
                max_amount = max([d['amount'] for d in past_data])
                if all(past_profits) and data['amount'] > max_amount * 2 and data['amount'] > 1000000000:
                    code_dict[code]['state'] = STATE_BULL
                    code_dict[code]['count'] = 0
                    code_dict[code]['bull_profit'] = profit
                    print_code_dict(code, today)

        elif state == STATE_BULL:
            code_dict[code]['count'] += 1
            if code_dict[code]['count'] >= 3: 
                future_data = get_past_data(reader, code, today, today + timedelta(days=15))
                future_data = convert_data_readable(code, future_data)
                is_success = False
                for f in future_data:
                    if (f['close_price'] - f['yesterday_close']) / f['yesterday_close'] * 100 > 5:
                        is_success = True
                        break
                print(today, code, ('SUCCESS' if is_success else 'failed'))
                code_dict[code]['state'] = STATE_NONE
            elif abs((data['close_price'] - data['yesterday_close']) / data['yesterday_close'] * 100) > 3:
                code_dict[code]['state'] = STATE_NONE
        #TODO: STATE_BUY: buy at start price and, if reach to 10% then sell it


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    #market_code = ['A006050']

    from_date = date(2019, 9, 1)
    until_date = date(2020, 1, 10)

    for code in market_code:
        code_dict[code] = {'state': STATE_NONE,
                            'bought_price': 0,
                            'bull_profit': 0,
                            'count': 0}

    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        start_today_trading(message_reader, market_code, from_date)
        from_date += timedelta(days=1)
