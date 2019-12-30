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
import stream_readwriter
import threading
import pandas as pd

from morning_server import message
from morning_server import stock_api
from morning_server import stream_readwriter
from morning.back_data import holidays
from morning.pipeline.converter import dt
from utils import time_converter

if len(sys.argv) < 2 and (sys.argv[1] == 'KOSPI' or sys.argv[1] == 'KOSDAQ'):
    print(sys.argv[0], '[KOSPI/KOSDAQ]')
    sys.exit(0)


from_date = date(2019, 12, 27)
until_date = date(2019, 12, 27)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market = message.KOSPI if sys.argv[1] == 'KOSPI' else message.KOSDAQ
kospi_code = stock_api.request_stock_code(message_reader, market)

df = pd.DataFrame(columns=['date', 'code', 'today_close', 'profit', 'highest_time', 'highest_profit', 'lowest_time', 'lowest_profit', 'today_amount', 'yesterday_amount', 'yesterday_cum_buy', 'yesterday_cum_sell', 'today_cum_buy', 'today_cum_sell', 'yesterday_rank'])

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)
    yesterday_datas = []
    for code in kospi_code:
        yesterday_data = stock_api.request_stock_day_data(message_reader, code, yesterday, yesterday)
        if len(yesterday_data) == 0:
            print('NO YESTERDAY DATA', code, from_date)
            continue
        yesterday_data = dt.cybos_stock_day_tick_convert(yesterday_data[0])
        yesterday_data['code'] = code
        yesterday_datas.append(yesterday_data)

        today_data = stock_api.request_stock_day_data(message_reader, code, from_date, from_date)
        if len(today_data) == 0:
            print('NO TODAY DATA', code, from_date)
            continue
        today_data = dt.cybos_stock_day_tick_convert(today_data[0])
        today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        if len(today_min_data) == 0:
            print('NO TODAY MIN DATA', code, from_date)
            continue

        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        today_min_data_c = sorted(today_min_data_c, key=lambda x: x['highest_price'], reverse=True)
        today_min_data_l = sorted(today_min_data_c, key=lambda x: x['lowest_price'])
        profit = float("%0.2f" % ((today_data['close_price'] - yesterday_data['close_price']) / yesterday_data['close_price'] * 100.0))
        highest_profit = float("%0.2f" % ((today_min_data_c[0]['highest_price'] - yesterday_data['close_price']) / yesterday_data['close_price'] * 100.0))
        lowest_profit = float("%0.2f" % ((today_min_data_l[0]['lowest_price'] - yesterday_data['close_price']) / yesterday_data['close_price'] * 100.0))
        highest_hour_min = today_min_data_c[0]['time']
        lowest_hour_min = today_min_data_l[0]['time']
        highest_time = datetime(from_date.year, from_date.month, from_date.day, int(highest_hour_min / 100), int(highest_hour_min % 100))
        lowest_time = datetime(from_date.year, from_date.month, from_date.day, int(lowest_hour_min / 100), int(lowest_hour_min % 100))
        df = df.append({'date': from_date,
                    'code': code,
                    'today_close': today_data['close_price'],
                    'profit': profit,
                    'highest_time': highest_time, 
                    'highest_profit': highest_profit,
                    'lowest_time': lowest_time,
                    'lowest_profit': lowest_profit,
                    'today_amount': today_data['amount'],
                    'yesterday_amount': yesterday_data['amount'], 
                    'yesterday_cum_buy': yesterday_data['cum_buy_volume'],
                    'yesterday_cum_sell': yesterday_data['cum_sell_volume'],
                    'today_cum_buy': today_data['cum_buy_volume'],
                    'today_cum_sell': today_data['cum_sell_volume']}, ignore_index=True)
    yesterday_datas = sorted(yesterday_datas, key=lambda x: x['amount'], reverse=True)
    for i, y in enumerate(yesterday_datas):
        df.loc[df['code'] == y['code'], 'yesterday_rank'] = i + 1

    from_date += timedelta(days=1)

df.to_excel('chooser_experiment_' + sys.argv[1] + '.xlsx')
