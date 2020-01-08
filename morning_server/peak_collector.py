from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime, time
import gevent
import socket
import sys
import threading
import pandas as pd
import numpy as np
from pymongo import MongoClient
from scipy.signal import find_peaks, peak_prominences

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db



def store_peak_information(peak_info):
    peak_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    db_data = list(peak_db['peak_info'].find({
                                    'code': peak_info['code'],
                                    'from_date': datetime.combine(peak_info['from_date'], time(0))}))
    peak_info['from_date'] = datetime.combine(peak_info['from_date'], time(0))
    peak_info['until_date'] = datetime.combine(peak_info['until_date'], time(0))
    if len(db_data) == 0:
        peak_db['peak_info'].insert_one(peak_info)
    else:
        print('found in DB', peak_info['code'])


def get_reversed(s):
    distance_from_mean = s.mean() - s
    return distance_from_mean + s.mean()


def calculate(x):
    peaks, _ = find_peaks(x, distance=10)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.002, peaks)
    prominences = np.extract(prominences > x.mean() * 0.002, prominences)
    return peaks, prominences


def get_peaks(avg_data, date_array, is_top):
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


def connect_min_data(today_min, tomorrow_min):
    price_array = np.array([])
    date_array = []
    volume_array = []
    current_volume = 0

    for tm in today_min:
        hlc = (tm['highest_price'] + tm['lowest_price'] + tm['close_price']) / 3
        price_array = np.append(price_array, np.array([hlc]))
        record_time = time_converter.intdate_to_datetime(tm['0'])
        record_time = record_time.replace(hour=int(tm['time'] / 100), minute=int(tm['time'] % 100))
        date_array.append(record_time)
        current_volume += tm['volume']
        volume_array.append(current_volume)

    for tomm in tomorrow_min:
        hlc = (tomm['highest_price'] + tomm['lowest_price'] + tomm['close_price']) / 3
        price_array = np.append(price_array, np.array([hlc]))
        record_time = time_converter.intdate_to_datetime(tomm['0'])
        record_time = record_time.replace(hour=int(tomm['time'] / 100), minute=int(tomm['time'] % 100))
        date_array.append(record_time)
        current_volume += tomm['volume']
        volume_array.append(current_volume)

    return price_array, date_array, volume_array


def create_peak_information(c):
    price_array, date_array, volume_array = connect_min_data(c['today_min_data'], c['tomorrow_min_data'])

    price_average = get_average_min_data(price_array)
    peaks_top = get_peaks(price_average, date_array, True)
    peaks_bottom = get_peaks(price_average, date_array, False)

    peak_data = {'code': c['code'],
                'from_date': c['date'],
                'until_date': c['until'],
                'peak': []}
    peak_data['peak'].append({'type': 0, 'time': date_array[0], 'volume': 0,
                    'price': c['yesterday_close']})
    for pt in peaks_top:
        peak_data['peak'].append({'type': 1, 'time': date_array[pt], 
                                'volume': volume_array[pt], 'price': price_array[pt]})

    for pb in peaks_bottom:
        peak_data['peak'].append({'type': 2, 'time': date_array[pb], 
                                'volume': volume_array[pb], 'price': price_array[pb]})
    peak_data['peak'].append({'type': 3, 'time': date_array[-1], 'volume': volume_array[-1],
                            'price': price_array[-1]})
    store_peak_information(peak_data)


def get_today_profit_statistics(min_data, yesterday_close):
    avg_prices = np.array([])
    for data in min_data:
        avg = (data['highest_price'] + data['lowest_price'] + data['close_price']) / 3
        avg_prices = np.append(avg_prices, np.array([avg]))
    return (avg_prices.mean() - yesterday_close) / yesterday_close * 100.


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



MAVG=20

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)


from_date = date(2018, 1, 1)
until_date = date(2019, 12, 31)

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)
    tomorrow = holidays.get_tomorrow(from_date)
    candidates = []

    for code in market_code:
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        if len(today_min_data) == 0:
            #print('NO TODAY MIN DATA', code, from_date)
            continue

        tomorrow_min_data = stock_api.request_stock_minute_data(message_reader, code, tomorrow, tomorrow)
        if len(tomorrow_min_data) <= 10:
            #print('NO or LESS TOMORROW MIN DATA', code, tomorrow)
            continue

        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*2), from_date)
        if MAVG * 2 * 0.6 > len(past_data):
            #print('PAST DATA too short', len(past_data), code)
            continue

        today_day_data = past_data[-1]
        past_data = past_data[:-1]

        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        tomorrow_min_data_c = []
        for tm in tomorrow_min_data:
            tomorrow_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        past_data_c = convert_data_readable(code, past_data)
        past_data_c = past_data_c[-(MAVG):]
        past_data_s = get_past_avg_numbers(code, past_data_c)
        today_profit_mean  = get_today_profit_statistics(today_min_data_c, past_data_c[-1]['close_price'])
        candidates.append({'code': code, 'date': from_date, 'until': tomorrow,
                            'yesterday_cum_buy_volume': past_data_c[-1]['cum_buy_volume'],
                            'yesterday_cum_sell_volume': past_data_c[-1]['cum_sell_volume'],
                            'yesterday_amount': past_data_c[-1]['amount'],
                            'amount_avg': past_data_s['amount_avg'],
                            'yesterday_mavg_price': past_data_c[-1]['moving_average'],
                            'yesterday_close': past_data_c[-1]['close_price'],
                            'today_min_data': today_min_data_c,
                            'tomorrow_min_data': tomorrow_min_data_c,
                            'today_profit_avg': today_profit_mean})

    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:150]
    final_candidates = []

    for c in candidates:
        if (c['yesterday_amount'] > c['amount_avg'] and
            c['yesterday_close'] > c['yesterday_mavg_price'] and
            c['yesterday_cum_buy_volume'] > c['yesterday_cum_sell_volume']):
            final_candidates.append(c)

    average_profit = 0
    average_std = 0
    for c in final_candidates:
        print(c['code'], 'profit', c['today_profit_avg'])
        average_profit += c['today_profit_avg']
        create_peak_information(c)

    if len(final_candidates):
        print(from_date, 'candidate count', len(final_candidates), 
                'profit mean', average_profit / len(final_candidates))

    from_date += timedelta(days=1)
