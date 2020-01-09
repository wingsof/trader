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

import price_comapre_plot


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


def connect_peaks(c, price_average, price_array, date_array, volume_array, pts, pbs, i):
    # Assert len(pbs) is not 0
    if len(pts) == 0 and len(pbs) == 0:
        return None

    peak_data = {'code': c['code'], 'from_date': c['date'],
                'until_date': c['until'], 'start_profit': 0, 'peak': []}
    peak_data['peak'].append({'type': 0, 'time': date_array[0], 'volume': 0,
                            'price': c['yesterday_close']})
    peaks_info = []
    for pt in pts:
        if pt > i: continue
        peaks_info.append({'type': 1, 'time': date_array[pt],
                                    'volume': volume_array[pt], 'price': price_array[pt]})
    
    for pb in pbs:
        peaks_info.append({'type': 2, 'time': date_array[pb], 
                                'volume': volume_array[pb], 'price': price_array[pb]})

    peaks_by_price_info = sorted(peaks_info, key=lambda x: x['price'])
    for i, pbpi in enumerate(peaks_by_price_info):
        pbpi['height_order'] = i + 1
    peaks_by_time_info = sorted(peaks_by_price_info, key=lambda x: x['time'])

    current_volume = 0
    for pbti in peaks_by_time_info:
        pbti['volume_diff'] = pbti['volume'] - current_volume
        current_volume = pbti['volume']

    peaks_by_volume_info = sorted(peaks_by_time_info, key=lambda x: x['volume_diff'])
    for i, pbvi in enumerate(peaks_by_volume_info):
        pbvi['volume_order'] = i + 1

    peak_data['peak'].extend(peaks_by_time_info)
    if len(peaks_by_time_info) > 0:
        start_peak_price = peaks_by_time_info[0]['price']
        peak_data['start_profit'] = (start_peak_price - c['yesterday_close']) / c['yesterday_close'] * 100
        if peak_data['start_profit'] > 30:
            print('Strange Profit', start_peak_price, c['yesterday_close'], c['code'], c['date'])
            print('price array', price_array)
    #print(peak_data)
    return peak_data
 

def get_nearest_peak(peak_data, start_time, until_time, full_data):
    # Find yesterday close and today first peak and which peak first?
    duration_m = until_time - start_time
    peak_db_data = peak_db_plus if peak_data['start_profit'] > 0 else peak_db_minus
    data_peak_pattern = [pd['type'] for pd in peak_data['peak']]
    data_height_pattern = [pd['height_order'] for pd in peak_data['peak'][1:]]
    data_volume_pattern = [pd['volume_order'] for pd in peak_data['peak'][1:]]

    matched_data = []
    # First phase: cut by duration
    for pdd in peak_db_data:
        peak_up_to_duration = [] 
        start_time = pdd['peak'][0]['time']
        for pd in pdd['peak']:
            if pd['time'] - start_time < duration_m: 
                peak_up_to_duration.append(pd)
            else:
                break

        peak_pattern = [pd['type'] for pd in peak_up_to_duration]
        if peak_pattern != data_peak_pattern:
            continue

        # Convert [7, 3, 4, 5] -> [4, 1, 2, 3]
        height_pattern = [pud['height_order'] for pud in peak_up_to_duration[1:]]
        hp_with_index = [[v, i] for i, v in enumerate(height_pattern)]
        hp_with_index = sorted(hp_with_index, key=lambda x: x[0])
        for i, hwi in enumerate(hp_with_index):
            height_pattern[hwi[1]] = i + 1
        if height_pattern != data_height_pattern:
            continue

        current_volume = 0
        volume_diff = []
        for pud in peak_up_to_duration[1:]:
            volume_diff.append(pud['volume'] - current_volume)
            current_volume = pud['volume']
        vd_with_index = [[v, i] for i, v in enumerate(volume_diff)]
        vd_with_index = sorted(vd_with_index, key=lambda x: x[0])
        for i, vwi in enumerate(vd_with_index):
            volume_diff[vwi[1]] = i + 1

        if volume_diff != data_volume_pattern:
            continue

        matched_data.append(pdd)

    if len(matched_data) > 0:
        print('MATCHED RESULT', peak_data['code'], 'peaks count', len(peak_data['peak']), until_time, len(matched_data))
        save_matched_data = []
        for md in matched_data:
            if peak_data['code'] in saved_data:
                if md['code'] in saved_data[peak_data['code']]:
                    continue
                else:
                    saved_data[peak_data['code']].append(md['code'])
                    save_matched_data.append(md)
            else:
                saved_data[peak_data['code']] = [md['code']]
                save_matched_data.append(md)
        if len(save_matched_data) > 0:
            price_comapre_plot.save(message_reader, peak_data, full_data, start_time, until_time, save_matched_data)


def find_match_peak(c):
    price_array, date_array, volume_array = connect_min_data(c['today_min_data'], c['tomorrow_min_data'])
    price_average = get_average_min_data(price_array)
    
    for i in range(len(price_average)):
        until_now_data = price_average[:i+1]
        peaks_top = get_peaks(until_now_data, True)
        peaks_bottom = get_peaks(until_now_data, False)
        if len(peaks_top) + len(peaks_bottom) >= 6: # Initial Setting
            da = date_array[:i+1]
            peak_data = connect_peaks(c, until_now_data, price_array[:i+1], da, volume_array[:i+1], peaks_top, peaks_bottom, i)
            if peak_data is not None:
                get_nearest_peak(peak_data, da[0], da[-1], (price_array, date_array, volume_array, price_average))
                             

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

print('START READ PEAK DB')
peak_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
peak_db_data = list(peak_db['peak_info'].find())
print('DB LEN', len(peak_db_data))
peak_db_plus = []
peak_db_minus = []
for pdd in peak_db_data:
    if pdd['start_profit'] > 0:
        peak_db_plus.append(pdd)
    else:
        peak_db_minus.append(pdd)

saved_data = dict()
print('DONE READ PEAK DB')

if len(peak_db_data) == 0:
    print('NO PEAK DATA')
    sys.exit(0)

from_date = date(2020, 1, 3)
until_date = date(2020, 1, 3)

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    print('RUN', from_date)
    yesterday = holidays.get_yesterday(from_date)
    tomorrow = holidays.get_tomorrow(from_date)
    candidates = []

    for code in market_code:
        
        past_data = stock_api.request_stock_day_data(message_reader, code, from_date - timedelta(days=MAVG*2), from_date)
        if MAVG * 2 * 0.6 > len(past_data):
            #print('PAST DATA too short', len(past_data), code)
            continue

        today_day_data = past_data[-1]
        past_data = past_data[:-1]

        past_data_c = convert_data_readable(code, past_data)
        past_data_c = past_data_c[-(MAVG):]
        past_data_s = get_past_avg_numbers(code, past_data_c)
        candidates.append({'code': code, 'date': from_date, 'until': tomorrow,
                            'yesterday_cum_buy_volume': past_data_c[-1]['cum_buy_volume'],
                            'yesterday_cum_sell_volume': past_data_c[-1]['cum_sell_volume'],
                            'yesterday_amount': past_data_c[-1]['amount'],
                            'amount_avg': past_data_s['amount_avg'],
                            'yesterday_mavg_price': past_data_c[-1]['moving_average'],
                            'yesterday_close': past_data_c[-1]['close_price']})

    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:150]
    final_candidates = []

    for c in candidates:
        if (c['yesterday_amount'] > c['amount_avg'] and
            c['yesterday_close'] > c['yesterday_mavg_price'] and
            c['yesterday_cum_buy_volume'] > c['yesterday_cum_sell_volume']):
            final_candidates.append(c)


    for fc in final_candidates:
        code = fc['code']
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        if len(today_min_data) == 0:
            print('NO TODAY MIN DATA', code, from_date)
            continue

        tomorrow_min_data = stock_api.request_stock_minute_data(message_reader, code, tomorrow, tomorrow)
        if len(tomorrow_min_data) <= 10:
            print('NO or LESS TOMORROW MIN DATA', code, tomorrow)
            continue

        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        tomorrow_min_data_c = []
        for tm in tomorrow_min_data:
            tomorrow_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        fc['today_min_data'] = today_min_data_c
        fc['tomorrow_min_data'] = tomorrow_min_data_c
        print('Try to find match', from_date, code)
        find_match_peak(fc)


    from_date += timedelta(days=1)
