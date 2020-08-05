from gevent import monkey; monkey.patch_all()
import gevent
from pymongo import MongoClient
from datetime import datetime, timedelta

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from clients.common import morning_client
from morning.back_data import holidays
from preloadtype import uni_current
from preloadtype import code_info
from utils import time_converter


_last_date = None
_market_codes = []
_yesterday_minute_data = {}
_yesterday_day_data = {}

loading = False
_request_stop = False
_current_spawn = None
_skip_ydata = False
_yesterday = 0


def is_skip_ydata():
    return _skip_ydata


def _get_yesterday_min_data(query_date, market_code):
    fail_count = 0 
    for progress, code in enumerate(market_code):
        if _request_stop:
            break
        print('collect yesterday minute data', f'{progress+1}/{len(market_code)}/{fail_count}', end='\r')
        mdata = morning_client.get_minute_data(code, query_date, query_date)
        if len(mdata) > 0:
            _yesterday_minute_data[code] = mdata
        else:
            fail_count += 1

    print('')


def _get_yesterday_day_data(query_date, market_code):
    fail_count = 0
    for progress, code in enumerate(market_code):
        if _request_stop:
            break
        print('collect yesterday day data', f'{progress+1}/{len(market_code)}/{fail_count}', end='\r')
        data = morning_client.get_past_day_data(code, query_date, query_date)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            _yesterday_day_data[code] = data
        else:
            fail_count += 1
    print('')


def start_preload(dt, skip_ydata):
    global _market_codes, loading, _yesterday
    print('Start Loading', dt)
    
    if len(_market_codes) == 0:
        # load infomration here, not depend on date
        _market_codes = morning_client.get_all_market_code()
        code_info.load_code_info(_market_codes)
        uni_current.load_uni_data(_market_codes)

    yesterday = holidays.get_yesterday(dt)
    _yesterday = time_converter.datetime_to_intdate(yesterday)
    print('Yesterday: ', yesterday)
    if not skip_ydata:
        _get_yesterday_day_data(yesterday, _market_codes)
        _get_yesterday_min_data(yesterday, _market_codes)
    loading = False


def load(dt, skip_ydata):
    global loading, _market_codes, _last_date, _request_stop, _current_spawn, _skip_ydata
    print('Load Data')
    _skip_ydata = skip_ydata

    dt = dt if dt.__class__.__name__ == 'date' else dt.date()

    if (_last_date is not None and
        _last_date == dt):
        print('already loaded preload data')
        return

    if loading:
        if _current_spawn is not None:
            print('Stop Current Loading')
            _request_stop = True
            gevent.joinall([_current_spawn])
            _current_spawn = None
            _request_stop = False
        else:
            print('Spawn is none but still loading')
            return


    loading = True
    _last_date = dt
    _current_spawn = gevent.spawn(start_preload, dt, skip_ydata)
    

def is_kospi(code):
    return code_info.is_kospi(code)


def get_corp_name(code):
    return code_info.get_corp_name(code)


def get_year_high(code, dt):
    return uni_current.get_year_high(code, dt)


def get_yesterday_amount(code):
    if code in _yesterday_day_data:
        return _yesterday_day_data[code]['amount']
    return 0


def get_yesterday_year_high(code):
    if _yesterday == 0:
        return 0
    return uni_current.get_year_high(code, _yesterday)


def get_yesterday_close(code):
    if code in _yesterday_day_data:
        return _yesterday_day_data[code]['close_price']
    return 0


if __name__ == '__main__':
    load(datetime(2020, 6, 15, 7, 0, 0), False)
    while loading:
        gevent.sleep(1)
    print('Done') 
    code = 'A005930'
    print('corp', get_corp_name(code))
    print('is_kospi', is_kospi(code))
    print('year high', get_yesterday_year_high(code))
    print('get_yesterday_close', get_yesterday_close(code))
    print('get_yesterday_amount', get_yesterday_amount(code))


    """
    _market_codes = morning_client.get_all_market_code()
    _get_yesterday_day_data(holidays.get_yesterday(datetime(2020, 6, 15, 7, 0, 0)), _market_codes)
    _get_yesterday_min_data(holidays.get_yesterday(datetime(2020, 6, 15, 7, 0, 0)), _market_codes)
    """
