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
from experiments import over_avg_long


if len(sys.argv) < 2 or not (sys.argv[1] == 'True' or sys.argv[1] == 'False'):
    print('Usage:', sys.argv[0], '[True|False]')
    sys.exit(0)

if sys.argv[1] == 'False':
    TEST_MODE = True
else:
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


if TEST_MODE:
    from_date = date(2019, 10, 1)
    until_date = date(2019, 11, 30)
else:
    from_date = date(2019, 1, 1)
    until_date = date(2020, 1, 1)

MAVG=20

#NOTES: A302430 무상증자로 반값, A138080 무상증자, A230980 가격 안맞음

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
if TEST_MODE:
    market_code = ['A246720']
    #market_code = ['A099410', 'A061040', 'A047310', 'A053660', 'A027050', 'A089970', 'A032685', 'A010240', 'A017890', 'A168330', 'A048470']

code_dict = dict()
records = []

#market_code = ['A086900']

NONE = 0
OVER_AVG = 1
LONG = 2


class CodeInfo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_today_min_data(code, from_date):
    today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
    if len(today_min_data) == 0:
        print('NO MIN DATA', code, from_date)
        return []
    today_min_data_c = []
    for tm in today_min_data:
        today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))
    return today_min_data_c


for code in market_code:
    code_dict[code] = CodeInfo(state=NONE, cut=0, buy_price=0, sell_price=0, buy_date=None, sell_date=None, over_days=0)

trades = []


def reset(c):
    c.state = NONE
    c.over_days = 0


while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)

    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*2), from_date)
        if MAVG * 2 * 0.6 > len(past_data):
            mprint('PAST DATA too short', len(past_data), code)
            continue
        elif past_data[-1]['0'] != time_converter.datetime_to_intdate(from_date):
            rprint(code, from_date, 'Cannot get today data')
            continue

        past_data_c = convert_data_readable(code, past_data)

        today_data = past_data_c[-1]
        past_data = past_data_c[:-1]

        yesterday_close = past_data[-1]['close_price']
        yesterday_over_mavg = past_data[-1]['moving_average'] < yesterday_close
        yesterday_close = past_data[-1]['close_price']
        is_over_mavg = (yesterday_over_mavg and
                        past_data[-2]['moving_average'] < past_data[-2]['close_price'] and
                        past_data[-3]['moving_average'] > past_data[-3]['close_price'])
        increase_candle = (past_data[-2]['start_price'] < past_data[-2]['close_price'] and past_data[-1]['start_price'] < past_data[-1]['close_price'])
        average_amount = np.array([past_data[-1]['amount'], past_data[-2]['amount']]).mean()
        day_before_yesterday_over_bull = (past_data[-2]['close_price'] - past_data[-3]['close_price']) / past_data[-3]['close_price'] * 100 > 20
        yesterday_over_bull = (past_data[-1]['close_price'] - past_data[-2]['close_price']) / past_data[-2]['close_price'] * 100 > 20
        #mprint(from_date, code, 'AVG', is_over_mavg, 'CANDLE', increase_candle)
        mprint(from_date, 'CLOSE', today_data['close_price'])
        if code_dict[code].state == NONE and is_over_mavg and increase_candle and not day_before_yesterday_over_bull and not yesterday_over_bull:
            code_dict[code].state = OVER_AVG
            code_dict[code].cut = max([past_data[-2]['highest_price'], past_data[-1]['highest_price']])
            mprint(from_date, code, 'OVER_AVG')

        if code_dict[code].state == OVER_AVG:
            today_increase = today_data['close_price'] >= today_data['start_price']
            is_under_mavg = today_data['moving_average'] > today_data['close_price']
            over_days = code_dict[code].over_days > 5
            today_over_bull = (today_data['highest_price'] - yesterday_close) / yesterday_close * 100. > 20
            #mprint(from_date, code, 'OVER_AVG', 'TODAY_INCREASE', today_increase, 'UNDER_AVG', is_under_mavg, 'CLOSE OVER CUT', today_data['close_price'] > code_dict[code].cut)
            if is_under_mavg or over_days or today_over_bull:
                reset(code_dict[code])
            elif not today_increase:
                if today_data['highest_price'] > code_dict[code].cut:
                    code_dict[code].cut = today_data['highest_price']
                    mprint(from_date, code, 'SET NEW HIGH')
                code_dict[code].over_days += 1
            else:
                if today_data['close_price'] > code_dict[code].cut:
                    code_dict[code].state = LONG
                    code_dict[code].buy_price = today_data['close_price']
                    code_dict[code].buy_date = from_date
                    mprint('\t', from_date, code, 'BUY', today_data['close_price'])
                code_dict[code].over_days += 1
        elif code_dict[code].state == LONG:
            # Use minute data
            min_data = get_today_min_data(code, from_date)
            if len(min_data) == 0:
                reset(code_dict[code])
                continue
            is_under_mavg = today_data['moving_average'] > today_data['close_price']
            open_price, sell_price, _ = over_avg_long.start_trade(min_data, yesterday_close)
            if sell_price == 0 and is_under_mavg:
                sell_price = today_data['close_price']

            if sell_price != 0:
                profit = (sell_price - code_dict[code].buy_price) / code_dict[code].buy_price * 100
                records.append({
                    'code': code,
                    'buy_price': code_dict[code].cut,
                    'sell_price': today_data['close_price'],
                    'buy_date': code_dict[code].buy_date,
                    'sell_date': from_date,
                    'profit': profit,
                })
                mprint('\t', from_date, code, 'SELL', sell_price, profit)
                reset(code_dict[code])
            
        rprint(from_date, 'process past data', f'{i+1}/{len(market_code)}', end='\r')
    rprint('')
    from_date += timedelta(days=1)

if not TEST_MODE:
    df = pd.DataFrame(records)
    df.to_excel('over_avg_set.xlsx')
