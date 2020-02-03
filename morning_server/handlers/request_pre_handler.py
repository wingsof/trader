from pymongo import MongoClient
from datetime import date, timedelta, datetime

from morning_server import message
from morning.back_data import fetch_stock_data
from morning.back_data.holidays import is_holidays, get_working_days, get_yesterday
from configs import db
from utils import time_converter


def _check_empty_date(days, vacancy_days, working_days):
    check_array = [None] * (len(working_days) + 1)
    # insert one more None to interate until the end
    for i, w in enumerate(working_days):
        if w not in days and w not in vacancy_days:
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

    return empty_periods


def _correct_date(d, now):
    if d > now.date():
        d = now.date()

    if is_holidays(d):
        d = get_yesterday(d)

    if d == now.date() and now.hour < 18:
        d = get_yesterday(d)

    return d


def sort_db_data(db_data, db_suffix):
    if db_suffix == '_M':
        return sorted(db_data, key=lambda x: x['0'] * 10000 + x['1'])

    return sorted(db_data, key=lambda x: x['0'])


def _get_data_from_db(code, from_date, until_date, db_suffix):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()
    now = datetime.now()
    from_date = _correct_date(from_date, now)
    until_date = _correct_date(until_date, now)

    stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    db_data = list(stock_db[code + db_suffix].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), '$lte': time_converter.datetime_to_intdate(until_date)}}))
    print(code + db_suffix, time_converter.datetime_to_intdate(from_date), time_converter.datetime_to_intdate(until_date))
    db_data = sort_db_data(db_data, db_suffix)
    days = [time_converter.intdate_to_datetime(d['0']).date() for d in db_data]
    days = list(dict.fromkeys(days))
    working_days = get_working_days(from_date, until_date)
    vacancy_data = list(stock_db[code + '_V'].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), '$lte': time_converter.datetime_to_intdate(until_date)}}))
    vacancy_days = [time_converter.intdate_to_datetime(d['0']).date() for d in vacancy_data]
    empties = _check_empty_date(days, vacancy_days, working_days)
    #print('DB DATA', len(db_data), 'EMPTIES', empties)
    return db_data, empties


def pre_handle_request(sock, header, body):
    method = header['method']
    if method == message.DAY_DATA:
        from_date = header['from']
        until_date = header['until']
        code = db.tr_code(header['code'])
        return _get_data_from_db(code, from_date, until_date, '_D')
    elif method == message.MINUTE_DATA:
        from_date = header['from']
        until_date = header['until']
        code = db.tr_code(header['code'])
        return _get_data_from_db(code, from_date, until_date, '_M')
    elif method == message.ABROAD_DATA:
        return None, None

    return None, None
