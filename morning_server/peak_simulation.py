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
from configs import db


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
        else:
            converted['moving_average'] = 0

        converted_data.append(converted)

    return converted_data


def get_past_avg_numbers(code, data):
    cum_buy_avg = 0
    cum_sell_avg = 0
    amount_avg = 0
    for c in data:
        cum_buy_avg += c['cum_buy_volume']
        cum_sell_avg += c['cum_sell_volume']
        amount_avg += c['amount']
    cum_buy_avg = cum_buy_avg / len(data)
    cum_sell_avg = cum_sell_avg / len(data)
    amount_avg = amount_avg / len(data)
    return {'code': code, 'cum_buy_avg': cum_buy_avg, 'cum_sell_avg': cum_sell_avg, 'amount_avg': amount_avg}


def get_reversed(s):
    distance_from_mean = s.mean() - s
    return distance_from_mean + s.mean()


def calculate(x):
    peaks, _ = find_peaks(x, distance=10)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.002, peaks)
    prominences = np.extract(prominences > x.mean() * 0.002, prominences)
    return peaks, prominences


def get_peaks(avg_data, is_top):
    if not is_top:
        prices = get_reversed(avg_data)
    else:
        prices = avg_data
    peaks, _ = calculate(prices)
    return peaks


def get_average_min_data(prices):
    avg_array = np.array([])
    price_array = np.array([])
    for p in prices:
        price_array = np.append(price_array, [p])
        if len(price_array) < 10:
            avg_array = np.append(avg_array, [price_array.mean()])
        else:
            avg_array = np.append(avg_array, [price_array[-10:].mean()])
    return avg_array


def get_peak_info(min_data):
    prices = [(md['highest_price'] + md['lowest_price'] + md['close_price']) / 3 for md in min_data]
    time_array = [md['time'] for md in min_data]
    price_average = get_average_min_data(prices)

    peaks_top = get_peaks(price_average, True)
    peaks_bottom = get_peaks(price_average, False)

    peaks_info = []
    peaks_info.append({'type': 0, 'price': prices[0], 'time': time_array[0]})
    for pt in peaks_top:
        peaks_info.append({'type': 1, 'price': prices[pt], 'time': time_array[pt]})

    for pb in peaks_bottom:
        peaks_info.append({'type': 2, 'price': prices[pb], 'time': time_array[pb]})

    peaks_by_price_info = sorted(peaks_info, key=lambda x: x['price'])
    for i, pbpi in enumerate(peaks_by_price_info):
        pbpi['height_order'] = i + 1

    peaks_by_time_info = sorted(peaks_by_price_info, key=lambda x: x['time'])
    type_pattern = [t['type'] for t in peaks_by_time_info]
    height_pattern = [p['height_order'] for p in peaks_by_time_info]
    time_array = [p['time'] for p in peaks_by_time_info]
    return time_array, type_pattern, height_pattern


def get_signal(is_plus, type_pattern, height_pattern, time_array, is_long, buy_time):
    query = {'plus': is_plus, 'type': type_pattern, 'height': height_pattern}
    peak_statistics = list(peak_db['peak_statistics'].find(query))
    db_data = list(peak_statistics)
    is_buy = False, None
    if len(db_data) > 0:
        db_data = db_data[0]
        if is_long:
            if type_pattern[-1] == 1:
                if db_data['mean'] > 1.:
                    is_buy = True, db_data
                else:
                    is_buy = False, db_data
            else:
                is_buy = True, db_data # Hold
        else:
            if db_data['mean'] > 1. and db_data['cv'] != np.nan and db_data['mean'] > db_data['cv']:
                is_buy = True, db_data

    return is_buy


peak_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']

from_date = date(2019, 1, 3)
until_date = date(2019, 1, 3)

MAVG=20

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)

trades = []

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)

    print('Processing', from_date)
    candidates = []
    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*2), from_date)
        if MAVG * 2 * 0.6 > len(past_data):
            #print('PAST DATA too short', len(past_data), code)
            continue

        today_day_data = past_data[-1]
        past_data = past_data[:-1]

        past_data_c = convert_data_readable(code, past_data)
        past_data_c = past_data_c[-(MAVG):]
        past_data_s = get_past_avg_numbers(code, past_data_c)
        candidates.append({'code': code, 'date': from_date,
                            'yesterday_cum_buy_volume': past_data_c[-1]['cum_buy_volume'],
                            'yesterday_cum_sell_volume': past_data_c[-1]['cum_sell_volume'],
                            'yesterday_amount': past_data_c[-1]['amount'],
                            'amount_avg': past_data_s['amount_avg'],
                            'yesterday_mavg_price': past_data_c[-1]['moving_average'],
                            'yesterday_close': past_data_c[-1]['close_price']})
        print('process past data', f'{i+1}/{len(market_code)}', end='\r')

    print('')
    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:150]
    final_candidates = []

    for c in candidates:
        if (c['yesterday_amount'] > c['amount_avg'] and
            c['yesterday_close'] > c['yesterday_mavg_price'] and
            c['yesterday_cum_buy_volume'] > c['yesterday_cum_sell_volume']):
            final_candidates.append(c)

    long_codes = {}
    for i, fc in enumerate(final_candidates):
        code = fc['code']
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        if len(today_min_data) == 0:
            #print('NO TODAY MIN DATA', code, from_date)
            continue

        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))
            today_min_data_c[-1]['code'] = code
            is_plus = fc['yesterday_close'] < today_min_data_c[0]['start_price']
            time_array, type_pattern, height_pattern = get_peak_info(today_min_data_c)
            price = today_min_data_c[-1]['close_price']

            is_buy, peak_expect = get_signal(is_plus, type_pattern, height_pattern, time_array, code in long_codes, (long_codes[code]['buy_time'] if code in long_codes else 0))

            if code in long_codes and not is_buy:
                long_codes[code]['sell_price'] = price
                long_codes[code]['sell_time'] = today_min_data_c[-1]['time']
                buy_price = long_codes[code]['buy_price']
                long_codes[code]['profit'] = (price - buy_price) / buy_price * 100.
                long_codes[code]['type'] = type_pattern
                long_codes[code]['height'] = height_pattern
                if peak_expect is not None:
                    long_codes[code]['sell_expect'] = peak_expect['mean'], peak_expect['cv']
                trades.append(long_codes[code].copy())
                long_codes.pop(code, None)
            elif code not in long_codes and is_buy:
                long_codes[code] = {'code': code,
                                    'date': from_date,
                                    'buy_time': today_min_data_c[-1]['time'],
                                    'sell_time': None,
                                    'buy_price': price,
                                    'expect': (peak_expect['mean'], peak_expect['cv']),
                                    'sell_expect': None,
                                    'sell_price': 0,
                                    'profit': 0,
                                    'type': None,
                                    'height': None}

        if code in long_codes: # Not sold
            is_plus = fc['yesterday_close'] < today_min_data_c[0]['start_price']
            type_pattern, height_pattern = get_peak_info(today_min_data_c)
            price = today_min_data_c[-1]['close_price']
            long_codes[code]['sell_price'] = price
            long_codes[code]['sell_time'] = today_min_data_c[-1]['time']
            buy_price = long_codes[code]['buy_price']
            long_codes[code]['profit'] = (price - buy_price) / buy_price * 100.
            long_codes[code]['type'] = type_pattern
            long_codes[code]['height'] = height_pattern
            trades.append(long_codes[code].copy())
            long_codes.pop(code, None)

        print('process final candidates', f'{i+1}/{len(final_candidates)}', end='\r')
    print('')
    from_date += timedelta(days=1)

df = pd.DataFrame(trades)
df.to_excel('peak_trade.xlsx')
