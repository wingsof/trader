from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
from datetime import date, datetime, time, timedelta
from pymongo import MongoClient
import numpy as np

from morning_server import message
from configs import db
from clients.common import morning_client
from morning.back_data import holidays
from morning.pipeline.converter import dt
from scipy.signal import find_peaks, peak_prominences

SECOND_UNIT=10


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


def get_three_sec_tick_avg(tick_data, current_datetime):
    from_datetime = current_datetime - timedelta(seconds=SECOND_UNIT)
    data = list(filter(lambda x: from_datetime < x['date'] <= current_datetime, tick_data)) 
    if len(data) > 0:
        price_mavg = np.array([d['current_price'] for d in data]).mean()
        amount = sum([d['current_price'] * d['volume'] for d in data])
        return price_mavg, amount, data[-1]['current_price']
    return 0, 0, 0


def start_meause_speed(today):
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    yesterday_list = get_yesterday_amount_rank(today)
    code_dict = dict()
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
        """
        ba_tick_data = filter_in_market_ba_tick(ba_tick_data, tick_data[0]['date'])

        if len(ba_tick_data) < 1000:
            print(ydata['code'], 'not enough filtered ba tick data', len(ba_tick_data))
            continue
        """
        code_dict[ydata['code']] = {'tick_data': tick_data,
                                    'yesterday_close': ydata['close_price'],
                                    'open_price': open_price,
                                    'price_array': [],
                                    'amount_array': [],
                                    'current_price': 0}

    print('\nstart')
    current_datetime = datetime.combine(today, time(9,0,3))
    trade_info = {'bought': False, 'code': '', 'price': 0}

    success = 0
    failed = 0
    total_profit = 0
    while current_datetime < datetime.combine(today, time(15,20)):
        speed_array = []
        #print(current_datetime)
        for k, v in code_dict.items():
            mavg, amount, price = get_three_sec_tick_avg(code_dict[k]['tick_data'], current_datetime)
            if mavg == 0:
                continue
            code_dict[k]['price_array'].append(mavg)
            code_dict[k]['amount_array'].append(amount)
            code_dict[k]['current_price'] = price

            if len(code_dict[k]['price_array']) > SECOND_UNIT:
                prev_price = code_dict[k]['price_array'][-SECOND_UNIT]
                speed_array.append({'code': k, 'profit': (mavg - prev_price) / prev_price * 100, 'amount': np.array(code_dict[k]['amount_array'][-SECOND_UNIT:]).sum()})

        if len(speed_array) > 30:
            if not trade_info['bought']:
                speed_array = sorted(speed_array, key=lambda x: x['profit'], reverse=True)
                for sa in speed_array:
                    if sa['amount'] > 10000000 * SECOND_UNIT and sa['profit'] >= 1:
                        is_bought = True 
                        trade_info['bought'] = True
                        trade_info['code'] = sa['code']
                        trade_info['price'] = code_dict[sa['code']]['current_price']
                        code_dict[sa['code']]['price_array'] = code_dict[sa['code']]['price_array'][-10:]
                        print(current_datetime, 'bought', 'code', sa['code'], 'price', trade_info['price'], 'speed profit', sa['profit'], 'time', current_datetime)
                        break
            else:
                code = trade_info['code']
                price_array = code_dict[code]['price_array']
                current_price = code_dict[code]['current_price']
                profit = (current_price - trade_info['price']) / trade_info['price'] * 100
                profit -= 0.25
                peaks = get_peaks(np.array(price_array))
                if len(peaks) > 0 or profit <= -0.5:
                    if profit > 0:
                        success += 1
                    else:
                        failed += 1
                    total_profit += profit
                    print(current_datetime, 'code', code, 'sell', current_price, 'profit', "{0:.2f}".format(profit), 'success', success, 'failed', failed, 'total', "{0:.2f}".format(total_profit))
                    trade_info['bought'] = False
                #else:
                #    print('current price', code_dict[code]['current_price'])
        current_datetime += timedelta(seconds=1)


if __name__ == '__main__':
    TODAY = date(2020, 2, 21)
    start_meause_speed(TODAY)
