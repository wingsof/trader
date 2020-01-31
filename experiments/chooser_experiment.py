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


def get_past_avg_numbers(data):
    cum_buy_avg = 0
    cum_sell_avg = 0
    amount_avg = 0
    for c in data:
        cum_buy_avg += c['cum_buy_volume']
        cum_sell_avg += c['cum_sell_volume']
        amount_avg += c['amount']
    cum_buy_avg = cum_buy_avg / len(data)
    cum_sell_avg = cum_sell_avg / len(data)
    amount_avg = amount_avg / len(data)
    return {'code': code, 'cum_buy_avg': cum_buy_avg, 'cum_sell_avg': cum_sell_avg, 'amount_avg': amount_avg}


def get_min_avg_numbers(data, is_highest, yesterday_data):
    today_min_data_sorted = None
    if is_highest:
        today_min_data_sorted = sorted(data, key=lambda x: x['highest_price'], reverse=True)
    else:
        today_min_data_sorted = sorted(data, key=lambda x: x['lowest_price'])
    key_value = 'highest_price' if is_highest else 'lowest_price'
    profit = float("%0.2f" % ((today_min_data_sorted[0][key_value] - yesterday_data['close_price']) / yesterday_data['close_price'] * 100.0))
    hour_min = today_min_data_sorted[0]['time']
    peak_time = datetime(from_date.year, from_date.month, from_date.day, int(hour_min / 100), int(hour_min % 100))
    return profit, peak_time


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    trend_prices = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        trend_prices = np.append(trend_prices, np.array([converted['close_price']]))

        if len(avg_prices) == days_for_ranking:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
        else:
            converted['moving_average'] = 0

        if len(trend_prices) == 5:  # Fixed
            converted['trend_moving_average'] = trend_prices.mean()
            trend_prices = trend_prices[1:]
        else:
            converted['trend_moving_average'] = 0

        converted_data.append(converted)

    return converted_data


if not (len(sys.argv) >= 3 and (sys.argv[1] == 'KOSPI' or sys.argv[1] == 'KOSDAQ') and int(sys.argv[2]) > 0):
    print(sys.argv[0], '[KOSPI/KOSDAQ] [MOVING AVERAGE DAYS]')
    sys.exit(0)

days_for_ranking = int(sys.argv[2])
max_days = max([days_for_ranking * 2]) # for mitigate noise datas

from_date = date(2019, 1, 1)
until_date = date(2019, 12, 27)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
sock.connect(server_address)

message_reader = stream_readwriter.MessageReader(sock)
message_reader.start()

market = message.KOSPI if sys.argv[1] == 'KOSPI' else message.KOSDAQ
market_code = stock_api.request_stock_code(message_reader, market)

df = pd.DataFrame(columns=['date', 'code', 'today_close', 'yesterday_close', 'profit', 'highest_time', 'highest_profit', 'lowest_time', 'lowest_profit', 'today_amount', 'yesterday_amount', 'yesterday_cum_buy', 'yesterday_cum_sell', 'today_cum_buy', 'today_cum_sell', 'amount_avg', 'cum_buy_avg', 'cum_sell_avg', 'avg_amount_rank', 'yesterday_rank', 'yesterday_moving_average', 'top_short', 'top_long', 'bottom_short', 'bottom_long'])

while from_date <= until_date:
    if holidays.is_holidays(from_date):
        from_date += timedelta(days=1)
        continue

    yesterday = holidays.get_yesterday(from_date)
    yesterday_datas = []
    avg_datas = []

    for code in market_code:
        past_data = stock_api.request_stock_day_data(message_reader, code, yesterday - timedelta(days=max_days), from_date)
        if max_days * 0.6 > len(past_data):
            print('PAST DATA too short', len(past_data), code)
            continue

        today_min_data = stock_api.request_stock_minute_data(message_reader, code, from_date, from_date)
        if len(today_min_data) == 0:
            print('NO TODAY MIN DATA', code, from_date)
            continue

        yesterday_min_data = stock_api.request_stock_minute_data(message_reader, code, yesterday, yesterday)
        if len(yesterday_min_data) <= 10:
            print('NO or LESS YESTERDAY MIN DATA', code, yesterday)
            continue

        converted_data = convert_data_readable(code, past_data)

        yesterday_data = converted_data[-2]
        yesterday_datas.append(yesterday_data)
        today_data = converted_data[-1]

        today_min_data_c = []
        for tm in today_min_data:
            today_min_data_c.append(dt.cybos_stock_day_tick_convert(tm))

        yesterday_min_data_c = []
        for ym in yesterday_min_data:
            yesterday_min_data_c.append(dt.cybos_stock_day_tick_convert(ym))

        profit = float("%0.2f" % ((today_data['close_price'] - yesterday_data['close_price']) / yesterday_data['close_price'] * 100.0))
        highest_profit, highest_time = get_min_avg_numbers(today_min_data_c, True, yesterday_data)
        lowest_profit, lowest_time = get_min_avg_numbers(today_min_data_c, False, yesterday_data)

        past_avg_data = converted_data[-(days_for_ranking + 1):-1]
        avg_numbers = get_past_avg_numbers(past_avg_data)
        avg_datas.append(avg_numbers)

        tf = trendfinder.TrendFinder(code, from_date, yesterday_min_data_c)
        top_short, top_long, bottom_short, bottom_long = tf.get_trend()

        df = df.append({'date': from_date,
                    'code': code,
                    'today_close': today_data['close_price'],
                    'yesterday_close': yesterday_data['close_price'],
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
                    'today_cum_sell': today_data['cum_sell_volume'],
                    'amount_avg': avg_numbers['amount_avg'],
                    'cum_buy_avg': avg_numbers['cum_buy_avg'],
                    'cum_sell_avg': avg_numbers['cum_sell_avg'],
                    'yesterday_moving_average': yesterday_data['moving_average'],
                    'top_short': top_short, 'top_long': top_long,
                    'bottom_short': bottom_short, 
                    'bottom_long': bottom_long}, ignore_index=True)

    yesterday_datas = sorted(yesterday_datas, key=lambda x: x['amount'], reverse=True)
    for i, y in enumerate(yesterday_datas):
        df.loc[df['code'] == y['code'], 'yesterday_rank'] = i + 1

    avg_datas = sorted(avg_datas, key=lambda x: x['amount_avg'], reverse=True)
    for i, y in enumerate(avg_datas):
        df.loc[df['code'] == y['code'], 'avg_amount_rank'] = i + 1


    from_date += timedelta(days=1)

df.to_excel('chooser_experiment_' + sys.argv[1] + '_' + str(days_for_ranking) + '.xlsx')
