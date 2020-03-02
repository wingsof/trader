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
from sklearn.linear_model import LinearRegression

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from configs import db

MAVG=20
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


def start_today_trading(reader, market_code, today):
    code_dict = dict()
    yesterday = holidays.get_yesterday(today)

    for progress, code in enumerate(market_code):
        print('collect past data', today, f'{progress+1}/{len(market_code)}', end='\r')
        past_data = get_past_data(reader, code, yesterday - timedelta(days=MAVG*4), yesterday)
        if len(past_data) < MAVG:
            continue
        past_data = convert_data_readable(code, past_data)
        yesterday_data = past_data[-1]
        code_dict[code] = {'past_data': past_data}
    print('')

    candidates = []
    for progress, (code, v) in enumerate(code_dict.items()): 
        past_data = v['past_data']
        last_mavg = [d['moving_average'] for d in past_data[-MAVG:]]
        X = np.arange(len(last_mavg)).reshape((-1,1))
        reg = LinearRegression().fit(X, np.array(last_mavg))
        if reg.coef_[0] > 0:
            candidates.append(code)

    skip_count = 0
    for code in candidates:
        past_data = code_dict[code]['past_data']
        #print([d['moving_average'] for d in past_data], [d['moving_average'] for d in past_data[-MAVG:]])
        if not all([d['close_price'] for d in past_data[-MAVG:]]) or not all([d['moving_average'] for d in past_data[-MAVG:]]):
            #print('SKIP')
            skip_count += 1
            continue

        past_mavg_data = np.array([d['moving_average'] for d in past_data[-MAVG:]])
        past_close_data = np.array([d['close_price'] for d in past_data[-MAVG:]])
        std_from_mavg = ((past_close_data - past_mavg_data) / past_mavg_data * 100).std()
        mean_from_mavg = ((past_close_data - past_mavg_data) / past_mavg_data * 100).mean()
        avg_amount = np.array([d['amount'] for d in past_data[-MAVG:]]).mean()
        if avg_amount == 0:
            continue

        future_data = get_past_data(reader, code, today, today + timedelta(days=90))
        if len(future_data) < 90 * 0.6:
            continue
        future_data = convert_data_readable(code, future_data)
        today_data = future_data[0]
        future_data = future_data[1:]
        future_close_price = (np.array([d['close_price'] for d in future_data]) - today_data['close_price']) / today_data['close_price'] * 100

        X = np.arange(len(future_close_price)).reshape((-1,1))
        reg = LinearRegression().fit(X, future_close_price)
        slope = reg.coef_[0]

        future_avg_amount = np.array([d['amount'] for d in future_data]).mean()
        if future_avg_amount == 0:
            continue

        future_high = max([d['highest_price'] for d in future_data])
        future_low = max([d['lowest_price'] for d in future_data])
        report.append({'code': code, 'date': today,
                        'today_close': today_data['close_price'],
                        'mean_from_mavg': mean_from_mavg, 'std_from_mavg': std_from_mavg,
                        'past_amount_avg': avg_amount, 'future_amount_avg': future_avg_amount,
                        'future_profit_slope': slope, 'future_high': future_high, 'future_low': future_low,
                        'max_profit': (future_high - today_data['close_price']) / today_data['close_price'] * 100,
                        'min_profit': (future_low - today_data['close_price']) / today_data['close_price'] * 100})
    print('SKIP COUNT', skip_count, 'candidate', len(candidates))


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    from_date = date(2019, 6, 1) 
    until_date = date(2019, 10, 1)
    #until_date = date(2018, 1, 3)

    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        start_today_trading(message_reader, market_code, from_date)
        from_date += timedelta(days=1)

    df = pd.DataFrame(report)
    #print(report)
    df.to_excel('stick_mavg_stat.xlsx')
