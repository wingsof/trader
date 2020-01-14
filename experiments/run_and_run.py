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



# run and run
# before x min determine what buy (speed, amount, < 5%)

results = []

def find_best(candidates, t):
    PROFIT_LIMIT = (2, 5)
    best_candidates = []
    for c in candidates:
        datas = []
        left_start_index = 0
        for i, data in enumerate(c['data']):
            if data['time'] <= t:
                datas.append(data)
            else:
                left_start_index = i
                break
        
        if len(datas) == 0:
            continue
        
        check_price = c['start_price']
        increase_trend = True
        amount = 0
        for data in datas: 
            amount += data['amount']
            if data['close_price'] < check_price:
                increase_trend = False
                break
            check_price = data['close_price']

        if not increase_trend:
            continue

        profit = (datas[-1]['close_price'] - c['start_price']) / c['start_price'] * 100
        best_candidates.append({'code': c['code'], 'amount': amount, 'profit': profit, 'close_price': datas[-1]['close_price'], 'data': c['data'][left_start_index:]})

    best_candidates = list(filter(lambda x: PROFIT_LIMIT[0] <= x['profit'] <= PROFIT_LIMIT[1], best_candidates))
    return sorted(best_candidates, key=lambda x: x['amount'], reverse=True)


def start_trade_simulation(final_candidates, t, d):
    for fc in final_candidates:
        is_done = False
        buy_price = fc['close_price']
        new_high = buy_price
        for data in fc['data']:
            cut_profit = (data['lowest_price'] - new_high) / new_high * 100
            if cut_profit < -1.:
                results.append({'code': fc['code'], 'buy': buy_price, 'sell': data['lowest_price'], 'time': data['time']})
                print(fc['code'], d, 'buy', buy_price, 'sell', data['lowest_price'], data['time'])
                is_done = True
                break

            if new_high < data['close_price']:
                new_high = data['close_price']

        if not is_done:
            results.append({'code': fc['code'], 'buy': buy_price, 'sell': fc['data'][-1]['close_price'], 'time': fc['data'][-1]['time']})
            #print(fc['code'], d, 'buy', buy_price, 'sell', fc['data'][-1]['close_price'])


determine_time = [904]#, 910, 915, 920, 930, 940, 950]

for det in determine_time:
    print(det)
    from_date = date(2019, 12, 1)
    until_date = date(2019, 12, 2)
    record_from, record_until = from_date, until_date
    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue

        #print('RUN', from_date)
        candidates = []

        for i, code in enumerate(market_code):
            today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
            if len(today_min_data) == 0:
                continue
            today_min_data_c = []
            for tm in today_min_data:
                today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))
            candidates.append({'code': code, 'data': today_min_data_c, 'start_price': today_min_data_c[0]['start_price']})
            #print(f'Collect {i}/{len(market_code)}', end='\r')

        print('Start Best Candidates')
        best_candidates = find_best(candidates, det)
        final_candidates = best_candidates[:5]
        start_trade_simulation(final_candidates, det, from_date)
        
        from_date += timedelta(days=1)
    print(det, np.array([(d['sell'] - d['buy']) / d['buy'] * 100 for d in results]).mean())
    results.clear()
        
