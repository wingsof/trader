from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
import time
import threading
import pandas as pd
import numpy as np
from pymongo import MongoClient

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from configs import db
import os.path


_message_reader = None
_mongo_collection = None
MAVG=20
_kosdaq_code = None
_kospi_code = None

def get_market_code(market_type=message.KOSDAQ):
    return stock_api.request_stock_code(get_reader(), market_type)

def get_all_market_code():
    global _kosdaq_code, _kospi_code
    market_code = []
    kosdaq_code = get_market_code()
    kospi_code = get_market_code(message.KOSPI)
    market_code.extend(kosdaq_code)
    market_code.extend(kospi_code)
    _kospi_code = kospi_code
    _kosdaq_code = kosdaq_code
    market_code = list(dict.fromkeys(market_code))
    return list(filter(lambda x: len(x) > 0 and x[1:].isdigit(), market_code))

def get_reader():
    if _message_reader is None:
        setup()

    return _message_reader


def get_collection():
    if _mongo_collection is None:
        db_setup()
    
    return _mongo_collection

def code_to_name(code):
    result = stock_api.request_code_to_name(get_reader(), code)
    if isinstance(result, list):
        if len(result) == 1:
            return result[0]
    return ''


def is_kospi_code(code):
    global _kospi_code
    if _kospi_code is not None and code in _kospi_code:
        return True
    return False


def get_save_filename(path, filename, ext):
    fullpath = os.path.join(path, filename + '.' + ext)
    prefix_num = 1
    while os.path.exists(fullpath):
        fullpath = os.path.join(path, filename + '_' + str(prefix_num) + '.' + ext)
        prefix_num += 1
    return fullpath


def get_ask_bid_price_unit(market_type, price):
    if market_type == message.KOSDAQ:
        if price < 1000:
            return 1
        elif 1000 <= price < 5000:
            return 5
        elif 5000 <= price < 10000:
            return 10
        elif 10000 <= price < 50000:
            return 50
        else:
            return 100
    elif market_type == message.KOSPI:
        if price < 1000:
            return 1
        elif 1000 <= price < 5000:
            return 5
        elif 5000 <= price < 10000:
            return 10
        elif 10000 <= price < 50000:
            return 50
        elif 50000 <= price < 100000:
            return 100
        elif 100000 <= price < 500000:
            return 500
        else:
            return 1000


def _convert_min_data_readable(code, min_data):
    converted_data = []
    for md in min_data:
        converted = dt.cybos_stock_day_tick_convert(md)
        converted['code'] = code
        converted_data.append(converted)

    return converted_data


def _convert_uni_current_data_readable(code, current_data):
    converted_data = []
    for d in current_data:
        converted = dt.cybos_stock_uni_current_tick_convert(d)
        converted_data.append(converted)
    return converted_data


def _convert_uni_day_data_readable(code, day_data):
    converted_data = []
    for d in day_data:
        converted = dt.cybos_stock_uni_day_tick_convert(d)
        converted['code'] = code
        converted_data.append(converted)
    return converted_data


def _convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    avg_volumes = np.array([])
    yesterday_close = 0
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        converted['date'] = time_converter.intdate_to_datetime(converted['0'])
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        avg_volumes = np.append(avg_volumes, np.array([converted['volume']]))

        if yesterday_close == 0:
            yesterday_close = converted['close_price']
            converted['yesterday_close'] = yesterday_close
        else:
            converted['yesterday_close'] = yesterday_close
            yesterday_close = converted['close_price']

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
            converted['volume_average'] = avg_volumes.mean()
            avg_volumes = avg_volumes[1:]
        else:
            converted['moving_average'] = 0
            converted['avg_volumes'] = 0

        converted_data.append(converted)

    return converted_data


def get_past_day_data(code, from_date, until_date, mavg=MAVG):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()

    past_data = stock_api.request_stock_day_data(get_reader(), code, from_date - timedelta(days=int(mavg*1.5)), until_date)
    past_data = _convert_data_readable(code, past_data)
    # until_date shall not be holiday

    cut_by_date_data = []
    for data in past_data:
        if from_date <= data['date'].date() <= until_date:
            cut_by_date_data.append(data)

    if holidays.count_of_working_days(from_date, until_date) > len(cut_by_date_data):
        print('get_past_day_data days not matched', code, from_date, until_date, 'data',
                "expected:", holidays.count_of_working_days(from_date, until_date), "actual:", len(cut_by_date_data))
        #return []

    return cut_by_date_data


def get_uni_current_period_data(code, from_date, until_date):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()
    uni_data = stock_api.request_stock_uni_current_period_data(get_reader(), code, from_date, until_date)
    return _convert_uni_current_data_readable(code, uni_data)


def get_uni_current_data(code):
    return _convert_uni_current_data_readable(code, stock_api.request_stock_uni_current_data(get_reader(), code))


def get_uni_day_period_data(code, from_date, until_date):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()
    uni_data = stock_api.request_stock_uni_day_period_data(get_reader(), code, from_date, until_date)
    return _convert_uni_day_data_readable(code, uni_data)


def get_uni_day_data(code):
    return _convert_uni_day_data_readable(code, stock_api.request_stock_uni_day_data(get_reader(), code))


def get_minute_data(code, from_date, until_date, t = 0):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()

    minute_data = stock_api.request_stock_minute_data(get_reader(), code, from_date, until_date) 
    minute_data = _convert_min_data_readable(code, minute_data)
    if t != 0:
        minute_data = list(filter(lambda x: x['time'] < t, minute_data))
    return minute_data


def get_today_minute_data(code):
    minute_data = stock_api.request_stock_today_data(get_reader(), code)
    return _convert_min_data_readable(code, minute_data)


def get_balance(): # return amount  {'balance': 1543974}
    result = stock_api.get_balance(get_reader())
    if 'balance' in result:
        return result['balance']
    
    return 0


def get_long_list():
    return stock_api.request_long_list(get_reader())


def get_yesterday_top_amount(dt):
    if dt.hour >= 18:
        tday = dt
        today_date = tday.year * 10000 + tday.month * 100 + tday.day
        codes = stock_api.request_yesterday_top_amount(get_reader(), today_date)
        if len(codes) > 0:
            return codes, True, today_date

    yday = holidays.get_yesterday(dt)
    yesterday_date = yday.year * 10000 + yday.month * 100 + yday.day
    codes = stock_api.request_yesterday_top_amount(get_reader(), yesterday_date)
    return codes, False, yesterday_date


def get_tick_data(code, tick_date):
    tick_date = tick_date if tick_date.__class__.__name__ == 'date' else tick_date.date()

    from_datetime = datetime.combine(tick_date, time(0,0))
    until_datetime = datetime.combine(tick_date + timedelta(days=1), time(0,0))
    data = list(get_collection()[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        if code.endswith(message.BIDASK_SUFFIX):
            converted = dt.cybos_stock_ba_tick_convert(td)
        else:
            converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


def setup():
    global _message_reader
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
            sock.connect(server_address)
            break
        except socket.error:
            print('Retrying connect to apiserver')
            gevent.sleep(1)

    _message_reader = stream_readwriter.MessageReader(sock)
    _message_reader.start()


def db_setup():
    global _mongo_collection
    _mongo_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

if __name__ == '__main__':
    print(get_uni_current_data('A005930'))
    #print(get_uni_day_data('A005930'))
    #print(get_uni_current_period_data('A005930', date(2020, 7, 31), date(2020, 8, 1)))
    #codes = get_all_market_code()
    #print(len(codes))
    #print(get_balance())
    #print(get_long_list())
    #print(get_today_minute_data('A005930'))
    #print(get_yesterday_top_amount())
    #result = get_past_day_data('A005930', date(2020, 7, 1), date(2020, 7, 8))
    #for data in result:
    #    print(data)
