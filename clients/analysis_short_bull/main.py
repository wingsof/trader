from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
from datetime import date, datetime, time, timedelta
from pymongo import MongoClient
import numpy as np

from morning_server import message
import pandas as pd
from configs import db
from clients.common import morning_client
from morning.back_data import holidays
from morning.pipeline.converter import dt
from scipy.signal import find_peaks, peak_prominences


def calculate(x):
    peaks, _ = find_peaks(x, distance=2)
    prominences = peak_prominences(x, peaks)[0]

    peaks = np.extract(prominences > x.mean() * 0.005, peaks)
    prominences = np.extract(prominences > x.mean() * 0.005, prominences)
    return peaks, prominences


def get_peaks(avg_data):
    peaks, _ = calculate(avg_data)
    return peaks


def filter_in_market_tick(tick_data):
    index = 0
    for i, d in enumerate(tick_data):
        if d['market_type'] == dt.MarketType.IN_MARKET:
            index = i
            break
    # remove pre market summary tick (index+1)
    return tick_data[index]['current_price'], tick_data[index+1:]


def filter_in_market_ba_tick(tick_data, t):
    index = 0
    for i, d in enumerate(tick_data):
        if d['date'] > t:
            index = i
            break
    return tick_data[index:]


def get_tick_data(code, today, db_collection):
    from_datetime = datetime.combine(today, time(0,0))
    until_datetime = datetime.combine(today + timedelta(days=1), time(0,0))
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        if code.endswith(message.BIDASK_SUFFIX):
            converted = dt.cybos_stock_ba_tick_convert(td)
        else:
            converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def get_yesterday_amount_rank(today):
    market_code = morning_client.get_market_code()
    yesterday = holidays.get_yesterday(today)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    # For testing
    yesterday_list = yesterday_list[:100]
    return yesterday_list


def get_tick_info(tick_data, current_datetime, secs):
    from_datetime = current_datetime - timedelta(seconds=secs)
    data = list(filter(lambda x: from_datetime < x['date'] <= current_datetime, tick_data)) 
    if len(data) > 0:
        prices = [d['current_price'] for d in data]
        amount = sum([d['current_price'] * d['volume'] for d in data])
        return data[0]['current_price'], max(prices), prices[-1] > prices[0], amount, data
    return 0, 0, False, 0, None


def get_tick_avg(tick_data, current_datetime, secs):
    from_datetime = current_datetime - timedelta(seconds=secs)
    data = list(filter(lambda x: from_datetime < x['date'] <= current_datetime, tick_data)) 
    if len(data) > 0:
        price_mavg = np.array([d['current_price'] for d in data]).mean()
        amount = sum([d['current_price'] * d['volume'] for d in data])
        return price_mavg, amount, data[-1]['current_price'], data[0]['current_price']
    return 0, 0, 0, 0


def start_meause_speed(today):
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    yesterday_list = get_yesterday_amount_rank(today)
    code_dict = dict()
    report = []
    for progress, ydata in enumerate(yesterday_list):
        print('collect tick data', f'{progress+1}/{len(yesterday_list)}', end='\r')
        tick_data = get_tick_data(ydata['code'], today, db_collection)
        #ba_tick_data = get_tick_data(ydata['code'] + message.BIDASK_SUFFIX, today, db_collection)
        if len(tick_data) < 1000:# or len(ba_tick_data) < 1000:
            print(ydata['code'], 'not enough tick data', 'tick', len(tick_data))
            continue
        open_price, tick_data = filter_in_market_tick(tick_data)
        if len(tick_data) < 1000:
            print(ydata['code'], 'not enough filtered tick data', len(tick_data))
            continue
        code_dict[ydata['code']] = {'tick_data': tick_data,
                                    'yesterday_close': ydata['close_price'],
                                    'open_price': open_price,
                                    'price_array': [],
                                    'amount_array': [],
                                    'current_price': 0}

    print('\nstart')
    last_profit = 0
    for k, v in code_dict.items():
        current_datetime = datetime.combine(today, time(9,1,0))
        while current_datetime < datetime.combine(today, time(15,20)):
            current_p, max_p, is_up, amount, data = get_tick_info(code_dict[k]['tick_data'], current_datetime, 30)
            if current_p == 0 or not is_up:
                current_datetime += timedelta(seconds=1)
                continue
            profit = (max_p - current_p) / current_p * 100
            if profit < 2:
                current_datetime += timedelta(seconds=1)
                continue

            print(current_datetime, profit, is_up, data[0]['current_price'], data[-1]['current_price'])
            price_avg_30, amount_30, price_30, open_30 = get_tick_avg(code_dict[k]['tick_data'], current_datetime - timedelta(seconds=30), 30)
            price_avg_10, amount_10, price_10, open_10 = get_tick_avg(code_dict[k]['tick_data'], current_datetime - timedelta(seconds=30), 10)
            if last_profit != profit:
                report.append({'code': k, 'time': current_datetime, 'profit': profit, 'price_avg_30': price_avg_30, 'amount_30': amount_30, 'open_30': open_30, 'close_30': price_30,
                    'price_avg_10': price_avg_10, 'amount_10': amount_10, 'open_10': open_10, 'close_10': price_10})
                last_profit = profit

            current_datetime += timedelta(seconds=1)
    df = pd.DataFrame(report)
    df.to_excel('analysis_short_bull.xlsx')


if __name__ == '__main__':
    TODAY = date(2020, 2, 21)
    start_meause_speed(TODAY)
