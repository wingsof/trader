"""
from_date = date(2019, 11, 1)
until_date = date(2020, 1, 15)

result
no condition:
summary 46.09803921568628 hold: 15.549019607843137 cut: 36.8235294117647

yesterday cum_buy_volume > cum_buy_sell:
summary 47.35294117647059 hold: 14.058823529411764 cut: 37.11764705882353

yesterday_close > 20 mavg
summary 47.490196078431374 hold: 11.019607843137255 cut: 40.07843137254902

yesterday amounts > 150 rank
summary 50.88235294117647 hold: 2.3529411764705883 cut: 45.6078431372549

mavg slope > 0
summary 48.80392156862745 hold: 8.96078431372549 cut: 40.72549019607843
average std 12.810871008399412 hold std 4.101462122428382 cut std 13.708560988212838


"""

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
from scipy.signal import find_peaks, peak_prominences
from pymongo import MongoClient

from morning.back_data import holidays
from morning_server import stock_api
from morning_server import stream_readwriter
from morning_server import message
from morning.pipeline.converter import dt
from utils import time_converter
from morning.config import db

from clients.hwani82 import code_chooser


MAVG=20
GOAL_PROFIT=4
CUT_PROFIT=-5


def get_past_data(reader, code, from_date, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, until_date)
    return past_data


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    avg_volumes = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        avg_volumes = np.append(avg_volumes, np.array([converted['volume']]))

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


def start_today_trading(reader, market_code, today, choosers):
    code_dict = dict()
    yesterday = holidays.get_yesterday(today)

    for progress, code in enumerate(market_code):
        print('collect past data', today, f'{progress+1}/{len(market_code)}', end='\r')
        past_data = get_past_data(reader, code, yesterday - timedelta(days=MAVG*3), yesterday)
        if len(past_data) == 0:
            continue
        past_data = convert_data_readable(code, past_data)
        yesterday_data = past_data[-1]
        code_dict[code] = {'past_data': past_data}
    print('')
    for c in choosers:
        new_code_dict = dict()
        result = c(reader, today, code_dict)
        for r in result:
            new_code_dict[r] = code_dict[r]
        code_dict = new_code_dict
    return list(code_dict.keys())


def evaluate_meet_goal(reader, candidates, today):
    all_count = 0
    meet_count = 0
    cut_count = 0
    print('candidates', candidates, today)
    for code in candidates:
        future_data = get_past_data(reader, code, today, today + timedelta(days=15))
        if len(future_data) < 3:
            continue
        all_count += 1
        future_data = convert_data_readable(code, future_data)
        #future_data = future_data[:3]
        open_price = future_data[0]['start_price']
        for f in future_data:
            if (f['lowest_price'] - open_price) / open_price * 100 <= CUT_PROFIT:
                cut_count += 1
                break
            elif (f['highest_price'] - open_price) / open_price * 100 >= GOAL_PROFIT:
                meet_count += 1 
                break
    return cut_count, meet_count, all_count


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    #market_code = ['A090430']
    average = []
    hold_average = []
    cut_average = []
    from_date = date(2019, 11, 1)
    until_date = date(2020, 1, 15)
    choosers = [code_chooser.negative_individual_investor]

    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        candidates = start_today_trading(message_reader, market_code, from_date, choosers)
        if len(candidates) == 0:
            print(from_date, 'NO CANDIDATES')
            continue
        cut, meet, all_count = evaluate_meet_goal(message_reader, candidates, from_date)
        percentage = int(meet/all_count*100)
        hold_percentage = int((all_count - cut - meet) / all_count * 100)
        cut_percentage = int(cut/all_count*100)
        print(from_date, f"{meet}/{all_count} per:{percentage}, hold:{hold_percentage}, cut:{cut_percentage}")
        average.append(percentage)
        hold_average.append(hold_percentage)
        cut_average.append(cut_percentage)
        from_date += timedelta(days=1)
    print('-' * 100)
    print('summary succeess', np.array(average).mean(), 'hold:', np.array(hold_average).mean(), 'cut:', np.array(cut_average).mean())
    print('average std', np.array(average).std(), 'hold std', np.array(hold_average).std(), 'cut std', np.array(cut_average).std())
    print('-' * 100)
