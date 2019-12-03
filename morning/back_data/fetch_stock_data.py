from pymongo import MongoClient
from morning.back_data.holidays import is_holidays, get_working_days
from morning.config import db
from utils import time_converter
from datetime import date, timedelta


def _insert_day_data(db, code, days, working_days, db_suffix):
    check_array = [None] * (len(working_days) + 1)
    # insert one more None to interate until the end
    #print('WORKING_DAYS', working_days)
    #print('DAYS', days)
    for i, w in enumerate(working_days):
        if w not in days:
            check_array[i] = w
    empty_from = None
    empty_until = None
    empty_periods = []
    for i, c in enumerate(check_array):
        if empty_from is None and c is not None:
            empty_from = c
        elif empty_from is not None and c is None:
            empty_until = check_array[i - 1]
            empty_periods.append((empty_from, empty_until))
            empty_from, empty_until = None, None

    if db is not None and len(empty_periods) > 0:
        from morning.cybos_api import stock_chart
        for p in empty_periods:
            length, data = stock_chart.get_day_period_data(code, p[0], p[1])
            if length > 0:
                print('INSERT', code + db_suffix, length)
                db[code + db_suffix].insert_many(data)

    return empty_periods


def get_day_period_data(code, from_date, until_date, db_suffix='_D'):
    stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']

    db_data = list(stock_db[code + db_suffix].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), '$lte': time_converter.datetime_to_intdate(until_date)}}))
    print('DB LEN', len(db_data))
    
    days = [time_converter.intdate_to_datetime(d['0']).date() for d in db_data]
    days = list(dict.fromkeys(days))
    working_days = get_working_days(from_date, until_date)
    empties = _insert_day_data(stock_db, code, days, working_days, db_suffix)
    if len(empties) > 0:
        db_data = list(stock_db[code + db_suffix].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), '$lte': time_converter.datetime_to_intdate(until_date)}}))        
    return db_data


def get_day_minute_period_data(code, from_date, until_date):
    return get_day_period_data(code, from_date, until_date, db_suffix='_M')


def get_day_past_highest(code, today, days):
    stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    yesterday = today - timedelta(days=1)
    while is_holidays(yesterday):
        yesterday -= timedelta(days=1)

    start = time_converter.datetime_to_intdate(yesterday - timedelta(days=days))
    end = time_converter.datetime_to_intdate(yesterday)
    cursor = stock_db[code + '_D'].find({'0': {'$gte':start, '$lt': end}})
    
    if cursor.count() == 0:
        return 0

    return max([d['3'] for d in list(cursor)])
