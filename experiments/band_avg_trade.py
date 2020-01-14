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


MAVG=20


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            converted['ma_20_upper_band'] = avg_prices.mean() + avg_prices.std() * 2
            converted['ma_20_bottom_band'] = avg_prices.mean() - avg_prices.std() * 2
            avg_prices = avg_prices[1:]
        else:
            converted['moving_average'] = 0
            converted['ma_20_upper_band'] = 0
            converted['ma_20_bottom_band'] = 0

        converted_data.append(converted)

    return converted_data


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)

from_date = date(2018, 1, 2)
until_date = date(2020, 1, 3)

long_codes = {}
trades = []
# {'buy_date', 'buy_price', 'buy_date', 'profit'}
while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    print('RUN', from_date)

    candidates = []

    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*2), from_date)
        if MAVG * 2 * 0.6 > len(past_data):
            #print('PAST DATA too short', len(past_data), code)
            continue

        past_data_c = convert_data_readable(code, past_data)
        today_data = past_data_c[-1]
        past_data = past_data_c[:-1]

        if code in long_codes:
            profit = (today_data['close_price'] - long_codes[code]['buy_price']) / long_codes[code]['buy_price'] * 100.
            long_codes[code]['profit'].append(profit)
            if today_data['ma_20_upper_band'] < today_data['close_price'] or profit <= -10.:
                trades.append({'code': code,
                                'buy_date': long_codes[code]['buy_date'],
                                'sell_date': from_date,
                                'buy_price': long_codes[code]['buy_price'],
                                'sell_price': today_data['close_price'],
                                'profit': long_codes[code]['profit'],
                                'trade_profit': profit})
                long_codes.pop(code, None)
        else:
            if (past_data[-1]['ma_20_bottom_band'] < past_data[-1]['close_price'] and
                today_data['ma_20_bottom_band'] > today_data['close_price']):
                candidates.append({'yesterday_amount': past_data[-1]['amount'], 'code': code,
                                    'today_close_price': today_data['close_price']})
        print(f'{i+1}/{len(market_code)}', end='\r')

    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:10]
    for c in candidates:
        long_codes[c['code']] = {'buy_date': from_date, 'buy_price': c['today_close_price'], 'profit': []}

    from_date += timedelta(days=1)

while holidays.is_holidays(from_date):
    from_date += timedelta(days=1)

for k, v in long_codes.items():
    today_data = stock_api.request_stock_day_data(message_reader, k, from_date, from_date)
    if len(today_data) >= 1:
        today_data = today_data[0]
        profit = (today_data['5'] - v['buy_price']) / v['buy_price'] * 100.
        v['profit'].append(profit)
        trades.append({'code': k,
                        'buy_date': v['buy_date'],
                        'sell_date': from_date,
                        'buy_price': v['buy_price'],
                        'sell_price': today_data['5'],
                        'profit': v['profit'],
                        'trade_profit': profit})
    else:
        print('today data wrong', from_date, k)

df = pd.DataFrame(trades)
df.to_excel('moving_average_band_20_kosdaq_10_cut.xlsx')
