from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences
import pandas as pd


def get_tick_data(code, from_datetime, until_datetime, db_collection):
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def search_tick(tick_data, price, qty):
    found = False
    for td in tick_data:
        if td['current_price'] == price and td['volume'] == qty:
            print(td)
            found = True

    if found:
        return True

    # depth 2 : ignore price
    #print('len', len(tick_data))
    for d in range(1, 10):
        #print('trying depth', d)
        for i, td in enumerate(tick_data[:-d]):
            vol = td['volume']
            rest_vol = 0
            amount = td['volume'] * td['current_price']
            for j in range(i+1, i+1+d):
                rest_vol += tick_data[j]['volume']
                amount += tick_data[j]['volume'] * tick_data[j]['current_price']

            if rest_vol + vol == qty:# and int(amount / (rest_vol + vol)) == price:
                print('Found ', 'avg', amount / (rest_vol + vol))
                print('price', td['current_price'], 'volume', td['volume'], 'buy/sell', td['buy_or_sell'], 'date', td['date'])
                for j in range(i+1, i+1+d):
                    print(j, 'price', tick_data[j]['current_price'], 'volume', tick_data[j]['volume'], 'buy/sell', tick_data[j]['buy_or_sell'])

                return True
    return False


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(sys.argv[0], 'code', 'time(2020-02-03 09:00)', 'price', 'qty')
        sys.exit(1)

    target_code = sys.argv[1]
    search_time = sys.argv[2]
    price = int(sys.argv[3])
    qty = int(sys.argv[4])

    search_time = datetime.strptime(search_time, '%Y-%m-%d %H:%M')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    tick_data = get_tick_data(target_code, search_time - timedelta(seconds=10), search_time + timedelta(seconds=60), db_collection)

    day_start_time = datetime(search_time.year, search_time.month, search_time.day, 9, 0)
    if len(tick_data) > 0:
        found = search_tick(tick_data, price, qty)

        if not found:
            tick_data = get_tick_data(target_code, day_start_time, day_start_time + timedelta(hours=10), db_collection)
            print('Exist tick data but cannot find matched', 'code start', tick_data[0]['date'], 'code end', tick_data[-1]['date'])
    else:
        tick_data = get_tick_data(target_code, day_start_time, day_start_time + timedelta(hours=10), db_collection)
        if len(tick_data) > 0:
            print('Cannot find tick data in that time', 'code start', tick_data[0]['date'], 'code end', tick_data[-1]['date'])
        else:
            print('No tick data')
