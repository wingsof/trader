from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
import time
import threading
import pandas as pd
import numpy as np
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)

from_date = date(2019, 1, 1)
until_date = date(2020, 1, 1)
record_from, record_until = from_date, until_date

# find moment over 1% profit 
moments = {}
# {'profit', 'buy_sell_rate', 'amount'}

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    print('RUN', from_date)
    yesterday = holidays.get_yesterday(from_date)
    candidates = []

    for code in market_code:
        past_data = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        if len(past_data) == 0:
            continue
        past_data = past_data[0]
        candidates.append({'code': code, 'yesterday_amount': past_data['7']})

    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:150]

    for c in candidates:
        today_min_data = stock_api.request_stock_minute_data(message_reader, c['code'], from_date, from_date)
        if len(today_min_data) <= 300:
            continue
        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        today_min_data = today_min_data_c
        initial_min_data = today_min_data[0]
        prev_cum_buy = initial_min_data['cum_buy_volume']
        prev_cum_sell = initial_min_data['cum_sell_volume']
        today_min_data = today_min_data[1:]
        for i, tm in enumerate(today_min_data):
            if len(today_min_data) > i + 2:
                cum_buy_diff = tm['cum_buy_volume'] - prev_cum_buy
                cum_sell_diff = tm['cum_sell_volume'] - prev_cum_sell
                if cum_buy_diff == 0 or cum_sell_diff == 0:
                    continue

                after_ten_min = today_min_data[i+2:i+12]
                max_price = max([atm['close_price'] for atm in after_ten_min])
                profit = (max_price - tm['close_price']) / tm['close_price'] * 100
                if not c['code'] in moments:
                    moments[c['code']] = []
                moments[c['code']].append({'date': tm['0'],
                                            'time': tm['time'],
                                            'profit': profit,
                                            'cum_rate': cum_buy_diff / cum_sell_diff})
                prev_cum_buy = tm['cum_buy_volume']
                prev_cum_sell = tm['cum_sell_volume']
    
    from_date += timedelta(days=1)

final_data = []
for k, v in moments.items():
    for vv in v:
        final_data.append({'code': k, 'date': vv['date'],
                            'time': vv['time'], 'profit': vv['profit'], 'cum_rate': vv['cum_rate']})

df = pd.DataFrame(final_data)
df.to_excel('moments_' + record_from.strftime('%Y%m%d_') + record_until.strftime('%Y%m%d') + '.xlsx')
