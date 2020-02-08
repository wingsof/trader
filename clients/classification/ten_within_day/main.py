"""
    1. search past data and set status of each code
    2. get long list and set status of each code status
    3. start subscribe for selected codes
    4. Do trades according to rules
"""

from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 3))))

from datetime import date, timedelta, datetime
import gevent
import socket
import scipy
import sys
import time
import threading
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db


def get_data(reader, code, d):
    prev_day = holidays.get_yesterday(d)
    past_data = stock_api.request_stock_day_data(reader, code, prev_day, d)
    if len(past_data) != 2:
        return None

    past_data_c = []
    for data in past_data:
        past_data_c.append(dt.cybos_stock_day_tick_convert(data))

    return past_data_c


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    search_from = date(2019, 12, 1)
    search_until = date(2020, 2, 6)

    result = []
    while search_from <= search_until:
        if holidays.is_holidays(search_from):
            search_from += timedelta(days=1)
            continue

        for progress, code in enumerate(market_code):
            print(search_from, f'{progress+1}/{len(market_code)}', end='\r')
            past_data = get_data(message_reader, code, search_from)
            if past_data is None:
                continue
            #risk = (past_data['highest_price'] - past_data['start_price']) / past_data['start_price'] * 100
            body_profit = (past_data[1]['highest_price'] - past_data[1]['start_price']) / past_data[1]['start_price'] * 100
            body_profit = float("{0:.2f}".format(body_profit))
            gap_profit = (past_data[1]['start_price'] - past_data[0]['close_price']) / past_data[0]['close_price'] * 100
            gap_profit = float("{0:.2f}".format(gap_profit))
            if abs(body_profit) >= 10 or abs(gap_profit) >= 10:
                result.append({'code': code, 'body': body_profit, 'date': search_from, 'amount': past_data[1]['amount'], 'gap': gap_profit})
        print('')
        search_from += timedelta(days=1)
    df = pd.DataFrame(result)
    df.to_excel('ten_within_day.xlsx')
