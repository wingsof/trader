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

def rprint(*kargs, **kwargs):
    print(*kargs, **kwargs)

def mprint(*kargs):
    #print(*kargs)
    pass


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


from_date = date(2019, 1, 1)
until_date = date(2020, 1, 7)

MAVG=20

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
code_dict = dict()
trades = []

#market_code = ['A086900']

NONE = 0
OVER_AVG = 1
OVER_PREV_HIGH = 2


class CodeInfo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


for code in market_code:
    code_dict[code] = CodeInfo(state=NONE, highest=0, cut=0, sdays=0, cross_price=0, cross_to_high=0, buy_open=0, buy_close=0, buy_state=False, buy_date=None, sell_date=None, amount=0, open_profits=[], close_profits=[])

trades = []

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)

    rprint('Processing', from_date)
    candidates = []
    watching = []
    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*3), from_date)
        if MAVG * 3 * 0.6 > len(past_data):
            mprint('PAST DATA too short', len(past_data), code)
            continue

        past_data_c = convert_data_readable(code, past_data)

        today_data = past_data_c[-1]
        past_data = past_data_c[:-1]

        yesterday_over_mavg = past_data[-1]['moving_average'] < past_data[-1]['close_price']
        yesterday_over_volume_mavg = past_data[-1]['volume_average'] < past_data[-1]['volume']
        is_over_mavg = (yesterday_over_mavg and
                        past_data[-2]['moving_average'] < past_data[-2]['close_price'] and
                        past_data[-3]['moving_average'] > past_data[-3]['close_price'])
        cross_price = past_data[-2]['close_price']
        is_buy_trend = past_data[-1]['cum_buy_volume'] > past_data[-1]['cum_sell_volume']

        if code_dict[code].state == NONE and is_over_mavg and yesterday_over_volume_mavg:
            code_dict[code].state = OVER_AVG
            mprint(from_date, 'OVER_AVG')
            code_dict[code].highest = past_data[-1]['highest_price']
            code_dict[code].cut = (past_data[-1]['highest_price'] + past_data[-1]['lowest_price']) / 2
        elif code_dict[code].state == OVER_AVG:
            if not yesterday_over_mavg or past_data[-1]['close_price'] < code_dict[code].cut:
                code_dict[code].state = NONE
                code_dict[code].sdays = 0
                mprint(from_date, 'UNDER_AVG')
            else:
                if code_dict[code].highest < past_data[-1]['close_price']:
                    if code_dict[code].sdays >= 2:
                        code_dict[code].state = OVER_PREV_HIGH
                        mprint(from_date, 'OVER_PREV_HIGH')
                        code_dict[code].amount = past_data[-1]['amount']
                        code_dict[code].sdays = 0
                    else:
                        code_dict[code].highest = past_data[-1]['highest_price']
                        code_dict[code].cut = (past_data[-1]['highest_price'] + past_data[-1]['lowest_price']) / 2
                        code_dict[code].sdays = 0
                        mprint(from_date, 'OVER_AVG new cut', code_dict[code].cut)
                else:
                    code_dict[code].sdays += 1
                    mprint(from_date, 'SUPPRESSED')
        elif code_dict[code].state == OVER_PREV_HIGH:
            if not code_dict[code].buy_state:
                code_dict[code].buy_state = True
                code_dict[code].buy_open = today_data['start_price']
                code_dict[code].buy_close = today_data['close_price']
                code_dict[code].buy_date = from_date
                mprint(from_date, 'BUY', today_data['start_price'], today_data['close_price'])
            else:
                if today_data['close_price'] < code_dict[code].cut:
                    code_dict[code].buy_state = False
                    code_dict[code].open_profits.append((today_data['close_price'] - code_dict[code].buy_open) / code_dict[code].buy_open * 100.)
                    code_dict[code].close_profits.append((today_data['close_price'] - code_dict[code].buy_close) / code_dict[code].buy_close * 100.)
                    code_dict[code].state = NONE
                    code_dict[code].sell_date = from_date
                    trades.append({'code': code, 'sell_price': today_data['close_price'], 'buy_date': code_dict[code].buy_date, 'sell_date': code_dict[code].sell_date,
                                    'buy_open': code_dict[code].buy_open, 'buy_close': code_dict[code].buy_close, 'amount': code_dict[code].amount})
                    mprint(from_date, 'SELL', today_data['close_price'])
                else:
                    mprint(from_date, 'HOLD', 'TODAY_CLOSE', today_data['close_price'], 'close_profit', (today_data['close_price'] - code_dict[code].buy_open) / code_dict[code].buy_open * 100.)
                    pass

                if code_dict[code].highest < today_data['highest_price']:
                    code_dict[code].cut = (today_data['highest_price'] + today_data['lowest_price']) / 2
                    mprint(from_date, 'HOLD new cut', code_dict[code].cut)
        rprint(from_date, 'process past data', f'{i+1}/{len(market_code)}', end='\r')
    rprint('')
    from_date += timedelta(days=1)

df = pd.DataFrame(trades)
df.to_excel('mavg_over_suppressed.xlsx')
