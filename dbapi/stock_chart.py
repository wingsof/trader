import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from datetime import datetime, timedelta
from pymongo import MongoClient

from dbapi import config


def get_day_period_data(code, startdate, enddate):
    db = MongoClient(config.MONGO_SERVER)['stock']
    start = time_converter.datetime_to_intdate(startdate)
    end = time_converter.datetime_to_intdate(enddate)

    cursor = db[code + '_D'].find({'0': {'$gte':start, '$lte': end}})

    return cursor.count(), list(cursor)


if __name__ == "__main__":
    date = datetime(2018, 10, 10)
    print(date - timedelta(days=30))
    l, d = get_day_period_data('A005930', date - timedelta(days=30), date)
    for i in d:
        print(i)

    print('count:', l)
