from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient
import matplotlib.pyplot as plt

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db

MAVG=20

def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
        else:
            converted['moving_average'] = 0

        converted_data.append(converted)

    return converted_data


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

code = 'A028300'
#market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
from_date = date(2020, 1, 3)
until_date = date(2020, 1, 8)

past_data = stock_api.request_stock_day_data(message_reader, code, from_date, until_date)
past_data_c = convert_data_readable(code, past_data)

current_price = past_data_c[0]['close_price']
past_data_c = past_data_c[1:]
x = np.linspace(-0.01, 0.01)
fig,ax = plt.subplots()
for data in past_data_c:
    # price per 1 share = amount / (cum_buy_volume + cum_sell_volume)
    # ax + by + c = 0    a = cum_buy_volume * pp1, b = cum_sell_volume * pp1
    price_per_share = data['amount'] / (data['cum_buy_volume'] + data['cum_sell_volume'])
    a = data['cum_buy_volume']
    b = data['cum_sell_volume']
    c = (data['close_price'] - current_price)
    print('amount', data['amount'], 'volume', (data['cum_buy_volume'] + data['cum_sell_volume']), a, b, c, c/b)

