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
    pass

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
until_date = date(2020, 1, 1)

MAVG=20

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
code_dict = dict()
records = []

#market_code = ['A086900']

NONE = 0
OVER_AVG = 1
OVER_PREV_HIGH = 2


class CodeInfo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


for code in market_code:
    code_dict[code] = CodeInfo(state=NONE, highest=0, keep_days=0, inst_buy_sum=0, highest_kdays=0, profit_from_buy=[], day_profits=[], day_candles=[], buy_price=0, buy_date=None, sell_date=None, tomorrow_profit_gap=0)

trades = []

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)

    candidates = []
    watching = []
    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*3), from_date)
        if MAVG * 3 * 0.6 > len(past_data):
            mprint('PAST DATA too short', len(past_data), code)
            continue
        elif past_data[-1]['0'] != time_converter.datetime_to_intdate(from_date):
            rprint(code, from_date, 'Cannot get today data')
            continue

        past_data_c = convert_data_readable(code, past_data)

        today_data = past_data_c[-1]
        past_data = past_data_c[:-1]

        yesterday_over_mavg = past_data[-1]['moving_average'] < past_data[-1]['close_price']
        today_over_mavg = today_data['moving_average'] < today_data['close_price']
        yesterday_over_volume_mavg = past_data[-1]['volume_average'] < past_data[-1]['volume']
        is_over_mavg = (yesterday_over_mavg and
                        past_data[-2]['moving_average'] < past_data[-2]['close_price'] and
                        past_data[-3]['moving_average'] > past_data[-3]['close_price'])
        inst_buy_array = [pd['institution_buy_volume'] for pd in past_data]
        inst_buy_sum = np.array(inst_buy_array[-5:])

        if code_dict[code].state == NONE and is_over_mavg:
            code_dict[code].state = OVER_AVG
            code_dict[code].inst_buy_sum = inst_buy_sum
            code_dict[code].highest_kdays = 0
            code_dict[code].keep_days = 0
            code_dict[code].buy_price = 0
            code_dict[code].tomorrow_profit_gap = 0
            code_dict[code].buy_date = None
            code_dict[code].sell_date = None
            code_dict[code].day_profits.clear()
            code_dict[code].day_candles.clear()
            code_dict[code].profit_from_buy.clear()
            code_dict[code].highest = past_data[-1]['highest_price']

            mprint(from_date, code, 'OVER_AVG')

        if code_dict[code].state == OVER_AVG:
            if not today_over_mavg:
                mprint('SELL')
                if code_dict[code].buy_price != 0:
                    if code_dict[code].keep_days == 1:
                        code_dict[code].tomorrow_profit_gap = (today_data['start_price'] - code_dict[code].buy_price) / code_dict[code].buy_price * 100.
                    mprint(from_date, code, 'UNDER_AVG', len(code_dict[code].day_profits), code_dict[code].day_profits)
                    records.append({'code': code,
                                    'highest': code_dict[code].highest,
                                    'buy_price': code_dict[code].buy_price,
                                    'keep_days': code_dict[code].keep_days,
                                    'buy_date': code_dict[code].buy_date,
                                    'sell_date': from_date,
                                    'inst_sum': code_dict[code].inst_buy_sum,
                                    'highest_kdays': code_dict[code].highest_kdays,
                                    'tomorrow_profit_gap': code_dict[code].tomorrow_profit_gap,
                                    'day_profits': code_dict[code].day_profits.copy(),
                                    'day_candles': code_dict[code].day_candles.copy(),
                                    'profit_from_buy': code_dict[code].profit_from_buy.copy()})
                code_dict[code].state = NONE

            else:
                if code_dict[code].buy_price == 0:
                    code_dict[code].buy_price = today_data['close_price']
                    code_dict[code].buy_date = from_date

                code_dict[code].keep_days += 1
                if code_dict[code].keep_days == 2:
                    code_dict[code].tomorrow_profit_gap = (today_data['start_price'] - code_dict[code].buy_price) / code_dict[code].buy_price * 100.

                if code_dict[code].highest < today_data['highest_price']:
                    code_dict[code].highest = today_data['highest_price']
                    code_dict[code].highest_kdays = code_dict[code].keep_days

                code_dict[code].day_candles.append((today_data['start_price'],
                                                    today_data['highest_price'],
                                                    today_data['lowest_price'],
                                                    today_data['close_price']))
                code_dict[code].day_profits.append((today_data['close_price'] - today_data['start_price']) / today_data['start_price'] * 100)
                code_dict[code].profit_from_buy.append((today_data['close_price'] - code_dict[code].buy_price) / code_dict[code].buy_price * 100)
                mprint('HOLD', len(code_dict[code].day_candles), len(code_dict[code].day_profits), code_dict[code].keep_days)

        rprint(from_date, 'process past data', f'{i+1}/{len(market_code)}', end='\r')
    rprint('')
    from_date += timedelta(days=1)

df = pd.DataFrame(records)
df.to_excel('mavg_statistics_2019.xlsx')
