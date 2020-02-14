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
from morning.config import db


_message_reader = None
MAVG=20

def get_market_code():
    return stock_api.request_stock_code(get_reader(), message.KOSDAQ)


def get_reader():
    if _message_reader is None:
        setup()

    return _message_reader


def _convert_min_data_readable(code, min_data):
    converted_data = []
    for md in min_data:
        converted = dt.cybos_stock_day_tick_convert(md)
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
                len(cut_by_date_data), 'expected', count_of_days)
        return []

    return cut_by_date_data


def get_minute_data(code, from_date, until_date, t = 0):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()

    minute_data = stock_api.request_stock_minute_data(get_reader(), code, from_date, until_date) 
    minute_data = _convert_min_data_readable(code, minute_data)
    if t != 0:
        minute_data = list(filter(lambda x: x['time'] < t, minute_data))
    return minute_data


def setup():
    global _message_reader
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    _message_reader = stream_readwriter.MessageReader(sock)
    _message_reader.start()


if __name__ == '__main__':
    result = get_past_day_data('A005930', date(2020, 2, 9), date(2020, 2, 12))
    for data in result:
        print(data)

