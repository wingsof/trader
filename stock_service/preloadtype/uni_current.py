from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta
from clients.common import morning_client
from morning_server import message
from utils import time_converter


_uni_data = {}


def load_uni_data(codes):
    now = datetime.now().date()
    for progress, code in enumerate(codes):
        #print('collect uni current data', f'{progress+1}/{len(codes)}', end='\r')
        uni_c = morning_client.get_uni_current_period_data(code, now - timedelta(days=365), now)
        if len(uni_c) == 0:
            continue

        _uni_data[code] = {}
        for d in uni_c:
            _uni_data[code][d['date']] = d

    print('')


def get_uni_current(code, intdate):
    if code in _uni_data:
        if intdate in _uni_data[code]:
            return _uni_data[code][intdate]
    return None
   

def get_uni_current_by_datetime(code, dt):
    t = time_converter.datetime_to_intdate(dt)
    return get_uni_current(code, t)


def get_uni_count():
    return len(_uni_data)


def get_year_high(code, intdate):
    if code in _uni_data:
        if intdate in _uni_data[code]:
            return _uni_data[code][intdate]['year_highest']
    return 0


def get_year_high_by_datetime(code, dt):
    t = time_converter.datetime_to_intdate(dt)
    return get_year_high(code, t)


