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

from_date = date(2018, 1, 1)
until_date = date(2019, 1, 3)
record_from, record_until = from_date, until_date

# find moment over 1% profit 
suppressed = {}
# {'profit', 'buy_sell_rate', 'amount'}

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    print('RUN', from_date)
    yesterday = holidays.get_yesterday(from_date)
    candidates = []

    for i, code in enumerate(market_code):
        past_data = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        print('GET DAY DATA', f'{i+1}/{len(market_code)}', end='\r')
        if len(past_data) == 0:
            continue
        past_data = past_data[0]
        candidates.append({'code': code, 'yesterday_amount': past_data['7']})
        
    candidates = sorted(candidates, key=lambda x: x['yesterday_amount'], reverse=True)
    candidates = candidates[:150]
    print('')
    for i, c in enumerate(candidates):
        print('Process Minute DATA', f'{i+1}/{len(candidates)}', end='\r')
        min_datas = stock_api.request_stock_minute_data(message_reader, c['code'], yesterday - timedelta(days=5), from_date)
        if len(min_datas) <= 360 * 3 or time_converter.intdate_to_datetime(min_datas[-1]['0']).date() != from_date:
            continue
        min_data_c = []
        for md in min_datas:
            min_data_c.append(dt.cybos_stock_day_tick_convert(md))

        min_data_c = sorted(min_data_c, key=lambda x: x['0'])
        current_date = 0
        min_data_by_day = []
        for mdc in min_data_c:
            if current_date != mdc['0']:
                current_date = mdc['0']
                min_data_by_day.append([mdc])
            else:
                min_data_by_day[-1].append(mdc)

        for mdbd in min_data_by_day:
            current_cum_buy, current_cum_sell = 0, 0
            amounts = np.array([])
            for i, day_min_data in enumerate(mdbd):
                if i == 0 or i == len(mdbd) - 1:
                    pass                    
                else:
                    amounts = np.append(amounts, np.array([day_min_data['amount']]))
            
            for i, day_min_data in enumerate(mdbd):
                if i == 0:
                    current_cum_buy, current_cum_sell = day_min_data['cum_buy_volume'], day_min_data['cum_sell_volume']
                elif i == len(mdbd) - 1:
                    pass                    
                else:
                    if day_min_data['amount'] > amounts.mean():
                        cum_buy_diff = day_min_data['cum_buy_volume'] - current_cum_buy
                        cum_sell_diff = day_min_data['cum_sell_volume'] - current_cum_sell
                        profit_gap = (day_min_data['close_price'] - day_min_data['start_price']) / day_min_data['start_price'] * 100
                        if not c['code'] in suppressed:
                            suppressed[c['code']] = []
                        suppressed[c['code']].append({'date': day_min_data['0'], 'time': day_min_data['time'],
                                                    'profit_gap': profit_gap, 'buy_volume': cum_buy_diff,
                                                    'sell_volume': cum_sell_diff, 'amount': day_min_data['amount']})
                        current_cum_buy, current_cum_sell = day_min_data['cum_buy_volume'], day_min_data['cum_sell_volume']
    
    from_date += timedelta(days=1)

final_data = []
for k, v in suppressed.items():
    for vv in v:
        vv['code'] = k
        final_data.append(vv)

df = pd.DataFrame(final_data)
df.to_csv('suppressed_' + record_from.strftime('%Y%m%d_') + record_until.strftime('%Y%m%d') + '.csv', encoding='utf-8', index=False)