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


def filter_in_market_tick(tick_data):
    index = 0
    for i, d in enumerate(tick_data):
        if d['market_type'] == dt.MarketType.IN_MARKET:
            index = i
            break
    return tick_data[index]['current_price'], tick_data[index+1:]


def get_tick_data(code, from_datetime, until_datetime, db_collection):
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


if __name__ == '__main__':
    code = 'A059090'
    from_datetime = datetime(2020, 2, 26, 14, 48, 49, 651000)
    until_datetime = datetime(2020, 2, 26, 14, 53, 32, 149000)

    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    tick_data = get_tick_data(code, from_datetime, until_datetime, db_collection)
    print(len(tick_data))
