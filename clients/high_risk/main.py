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

from clients.high_risk import code_chooser


MAVG=20
GOAL_PROFIT=1.3
CUT_PROFIT=-1.0


def get_past_data(reader, code, from_date, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, until_date)
    return past_data


def start_today_trading(reader, market_code, today, choosers):
    code_dict = dict()
    yesterday = holidays.get_yesterday(today)

    by_amounts = []
    for progress, code in enumerate(market_code):
        print('collect past data', today, f'{progress+1}/{len(market_code)}', end='\r')

        yesterday_data = stock_api.request_stock_day_data(reader, code, yesterday, yesterday)
        if len(yesterday_data) != 1:
            continue
        elif yesterday_data[0]['5'] < 900:
            continue

        code_dict[code] = {'code': code, 'past_min_data': [], 'today_min_data': None, 'time': 0, 'yesterday_close': yesterday_data[0]['5'], 'today_gap': 0, 'until_now_profit': 0}
        min_req_from = today - timedelta(days=10)
        min_req_until = today
        while min_req_from <= min_req_until:
            if holidays.is_holidays(min_req_from):
                min_req_from += timedelta(days=1)
                continue

            min_data = stock_api.request_stock_minute_data(reader, code, min_req_from, min_req_from)
            if len(min_data) > 0:
                min_data_c = []
                for md in min_data:
                    min_data_c.append(dt.cybos_stock_day_tick_convert(md))
                code_dict[code]['past_min_data'].append(min_data_c)
            min_req_from += timedelta(days=1)

        if len(code_dict[code]['past_min_data']) > 5:
            code_dict[code]['today_min_data'] = code_dict[code]['past_min_data'][-1]
            code_dict[code]['today_gap'] = (code_dict[code]['today_min_data'][0]['start_price'] - code_dict[code]['yesterday_close']) / code_dict[code]['yesterday_close'] * 100
            code_dict[code]['past_min_data'] = code_dict[code]['past_min_data'][:-1]
        else:
            #print('not enough data', code)
            code_dict.pop(code, None)

    print('')

    for c in choosers:
        new_code_dict = dict()
        result = c(reader, code_dict)
        for r in result:
            new_code_dict[r] = code_dict[r]
        code_dict = new_code_dict

    return code_dict


# candidates is list of {'code': code, 'today_min_data': min_data, 'time': time}
def evaluate_meet_goal(reader, candidates):
    all_count = 0
    meet_count = 0
    cut_count = 0
    loss_codes = []
    success_codes = []
    for code, c in candidates.items():
        data = c['today_min_data']
        all_count += 1
        start_price = 0
        for d in data:
            if start_price == 0:
                if d['time'] >= c['time']:
                    start_price = d['close_price']
            else:
                lowest_profit = (d['lowest_price'] - start_price) / start_price * 100
                highest_profit = (d['highest_price'] - start_price) / start_price * 100
                if CUT_PROFIT >= lowest_profit:
                    cut_count += 1
                    loss_codes.append({'code': code, 'time': c['time'], 'amount': c['amount'],
                        'today_gap': c['today_gap'], 'until_now_profit': c['until_now_profit']})
                    break
                elif GOAL_PROFIT <= highest_profit:
                    success_codes.append({'code': code, 'time': c['time'],
                        'amount': c['amount'], 'today_gap': c['today_gap'], 'until_now_profit': c['until_now_profit']})
                    meet_count += 1
                    break
    return cut_count, meet_count, all_count, loss_codes, success_codes


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    #market_code = ['A051490']
    average = []
    hold_average = []
    cut_average = []
    from_date = date(2020, 1, 1)
    until_date = date(2020, 2, 5)
    choosers = [code_chooser.same_time_over_volume]

    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        candidates = start_today_trading(message_reader, market_code, from_date, choosers)
        if len(candidates) == 0:
            print(from_date, 'NO CANDIDATES')
            from_date += timedelta(days=1)
            continue
        cut, meet, all_count, loss_codes, success_codes = evaluate_meet_goal(message_reader, candidates)
        percentage = int(meet/all_count*100)
        hold_percentage = int((all_count - cut - meet) / all_count * 100)
        cut_percentage = int(cut/all_count*100)
        print(from_date, f"{meet}/{all_count} per:{percentage}, hold:{hold_percentage}, cut:{cut_percentage}")
        print('-' * 30, 'loss', '-' * 30)
        for lc in loss_codes:
            print(lc['code'], 'time', lc['time'], 'amount', lc['amount'], 'gap', lc['today_gap'], 'until_now', lc['until_now_profit'])
        print('-' * 30, 'success', '-' * 30)
        for lc in success_codes:
            print(lc['code'], 'time', lc['time'], 'amount', lc['amount'], 'gap', lc['today_gap'], 'until_now', lc['until_now_profit'])
        print('-' * 30, 'success', '-' * 30)
        average.append(percentage)
        hold_average.append(hold_percentage)
        cut_average.append(cut_percentage)
        from_date += timedelta(days=1)

    print('-' * 100)
    print('summary succeess', np.array(average).mean(), 'hold:', np.array(hold_average).mean(), 'cut:', np.array(cut_average).mean())
    print('average std', np.array(average).std(), 'hold std', np.array(hold_average).std(), 'cut std', np.array(cut_average).std())
    print('-' * 100)
