from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta, datetime
import gevent
import socket
import sys
from datetime import date
import time
import threading
import pandas as pd
import numpy as np

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter
from morning_server import trendfinder


def check_by_time(group_data, min_data, by_time):
    by_time_data = []
    for data in min_data:
        for d in data:
            if int(d['time'] / 100) >= by_time:
                by_time_data.append({
                    'code': d['code'], 'amount': d['amount'], 'time': d['time'],
                    'buy': d['cum_buy_volume'], 'sell': d['cum_sell_volume']})
                break
    by_time_data = sorted(by_time_data, key=lambda x: x['amount'], reverse=True)
    by_time_data = by_time_data[:150]

    codes = []
    for data in by_time_data:
        if data['buy'] > data['sell']:
            codes.append(data)
    codes = codes[:150]

    diff = set(group_data).difference(set([d['code'] for d in codes]))
    return (1 - (len(diff) / len(group_data))) * 100 # careful, not contained rate
    

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)


from_date = date(2019, 10, 1)
until_date = date(2019, 12, 31)

df = None

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    today_data = []
    print(from_date)
    for code in market_code:
        data = stock_api.request_stock_day_data(message_reader, code, from_date, from_date)
        if len(data) > 0:
            data[0]['code'] = code
            today_data.append(dt.cybos_stock_day_tick_convert(data[0]))

    today_data = sorted(today_data, key=lambda x: x['amount'], reverse=True)
    today_profit_data = []
    for t in today_data:
        if t['close_price'] > t['start_price']:
            today_profit_data.append(t)
            if len(today_profit_data) > 150:
                break
    

    today_codes = [d['code'] for d in today_profit_data]
    print('DONE code')
    today_min_data = []
    for code in market_code:
        today_min = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        today_min_c = []
        for tm in today_min:
            tm['code'] = code
            today_min_c.append(dt.cybos_stock_day_tick_convert(tm))

        today_min_data.append(today_min_c)
    print('MIN DATA Collect done')
    found = True
    for i in range(20):
        if today_min_data[i][0]['time'] < 1000:
            found = False
            break
    if found: 
        print('Assume today start at 10', from_date)
        from_date += timedelta(days=1)
        continue

    by_hours = [10, 11, 12, 13, 14, 15]
    by_hour_result = dict(from_date=from_date)
    for by_hour in by_hours:
        by_hour_result[str(by_hour)] = float("{0:.2f}".format(check_by_time(today_codes, today_min_data, by_hour)))

    print(by_hour_result)

    if df is None:
        df = pd.DataFrame(by_hour_result, index=[0])
    else:
        df = df.append(by_hour_result, ignore_index=True)
    from_date += timedelta(days=1)

df.to_excel('amount_guess_summary_20190601_20191231.xlsx')


    


