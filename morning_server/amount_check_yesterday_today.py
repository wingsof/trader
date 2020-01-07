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
    yesterday_data = []
    yesterday = holidays.get_yesterday(from_date)
    print(from_date)
    for code in market_code:
        ydata = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        if len(ydata) > 0:
            ydata[0]['code'] = code
            yesterday_data.append(dt.cybos_stock_day_tick_convert(ydata[0]))

        data = stock_api.request_stock_day_data(message_reader, code, from_date, from_date)
        if len(data) > 0:
            data[0]['code'] = code
            today_data.append(dt.cybos_stock_day_tick_convert(data[0]))

    today_data = sorted(today_data, key=lambda x: x['amount'], reverse=True)
    today_data = today_data[:150]

    yesterday_data = sorted(yesterday_data, key=lambda x: x['amount'], reverse=True)
    yesterday_data = yesterday_data[:300]

    #yesterday_codes = [d['code'] for d in yesterday_data]
    yesterday_codes = []
    for yd in yesterday_data:
        if yd['cum_buy_volume'] > yd['cum_sell_volume']:
            yesterday_codes.append(yd['code'])

    today_codes = [d['code'] for d in today_data]

    print('DONE code')
    # How many yesterday codes are in today's amount rank
    diff = set(yesterday_codes).difference(set(today_codes))

    result = {'diff': ((len(yesterday_codes) - len(diff)) / len(yesterday_codes)) * 100}
    #result = {'diff': (len(diff) / len(today_codes)) * 100}
    if df is None:
        df = pd.DataFrame(result, index=[0])
    else:
        df = df.append(result, ignore_index=True)
    from_date += timedelta(days=1)

df.to_excel('yesterday_amount_today.xlsx')


    


