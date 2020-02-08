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


MAVG=120

BULL_PROFIT = 5
code_dict = dict()
STATE_UNKNOWN = -1
STATE_NONE = 0
STATE_BULL = 1
STATE_BOUGHT = 2
report = []

def get_past_data(reader, code, from_date, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, until_date)
    return past_data


def convert_data_readable(code, past_data):
    converted_data = {}
    converted_list = []
    avg_prices = np.array([])
    avg_volumes = np.array([])
    yesterday_close = 0
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        avg_volumes = np.append(avg_volumes, np.array([converted['volume']]))

        if yesterday_close == 0:
            yesterday_close = converted['close_price']
            converted['yesterday_close'] = yesterday_close
        else:
            converted['yesterday_close'] = yesterday_close
            yesterday_close = converted['close_price']

        if len(avg_prices) == MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
            converted['volume_average'] = avg_volumes.mean()
            avg_volumes = avg_volumes[1:]
        else:
            converted['moving_average'] = 0
            converted['avg_volumes'] = 0

        if converted['0'] not in converted_data:
            converted_data[converted['0']] = converted
        converted_list.append(converted)

    return converted_data, converted_list


def start_today_trading(reader, market_code, today):
    today_d = time_converter.datetime_to_intdate(today)

    for code in market_code:
        if today_d not in code_dict[code]['data']:
            continue
        elif code_dict[code]['state'] == STATE_BOUGHT:
            continue
        elif code_dict[code]['data'][today_d]['moving_average'] == 0:
            continue
        
        data = code_dict[code]['data'][today_d]

        if code_dict[code]['state'] == STATE_UNKNOWN:
            if data['start_price'] < data['moving_average'] and data['close_price'] < data['moving_average']:
                code_dict[code]['state'] = STATE_NONE
            else:
                continue


        bull_profit = (data['close_price'] - data['yesterday_close']) / data['yesterday_close'] * 100

        code_dict[code]['today_bull'] = bull_profit
        code_dict[code]['mvg'] = data['moving_average']
        over_avg = data['start_price'] > data['moving_average'] and data['close_price'] > data['moving_average']

        if code_dict[code]['state'] == STATE_NONE:
            bull_distance = (today - code_dict[code]['last_bull_date']).days if code_dict[code]['last_bull_date'] is not None else 0
            if bull_profit >= BULL_PROFIT:
                if bull_profit >= 20 and over_avg and data['amount'] >= 30000000000 and bull_distance > 10:
                    code_dict[code]['buy_price'] = data['start_price']
                    code_dict[code]['amount'] = data['amount']
                    code_dict[code]['state'] = STATE_BULL
                    code_dict[code]['setdate'] = today
                    code_dict[code]['highest'] = data['highest_price']
                else:
                    code_dict[code]['last_bull_date'] = today
        elif code_dict[code]['state'] == STATE_BULL:
            distance = (today - code_dict[code]['setdate']).days
            again_bull = bull_profit >= BULL_PROFIT and data['amount'] >= 30000000000 and data['amount'] > code_dict[code]['amount']
            if distance > 6 and again_bull and data['close_price'] > code_dict[code]['highest']:
                #print('again', data['start_price'])
                code_dict[code]['buy_price'] = data['start_price']
                code_dict[code]['amount'] = data['amount']
                code_dict[code]['setdate'] = today
                code_dict[code]['highest'] = data['highest_price']
            elif data['lowest_price'] <= code_dict[code]['buy_price']:
                code_dict[code]['state'] = STATE_BOUGHT
                code_dict[code]['buy_date'] = today

            if data['highest_price'] > code_dict[code]['highest']:
                code_dict[code]['highest'] = data['highest_price']


def set_first_over_mavg(reader, market_code, search_from, search_until):
    for progress, code in enumerate(market_code):
        print('collect past data', f'{progress+1}/{len(market_code)}', end='\r')
        past_data = get_past_data(reader, code, search_from - timedelta(days=MAVG*2), search_until + timedelta(days=90))
        past_data, data_list = convert_data_readable(code, past_data)
        code_dict[code]['data'] = past_data
        code_dict[code]['data_list'] = data_list
    print('')


def evaluate_meet_goal(reader, today):
    meet_count = 0
    cut_count = 0

    today_d = time_converter.datetime_to_intdate(today)

    for code in market_code:
        if code_dict[code]['state'] != STATE_BOUGHT or code_dict[code]['buy_date'] == today:
            continue
        elif today_d not in code_dict[code]['data']:
            continue

        data = code_dict[code]['data'][today_d]
        buy_price = code_dict[code]['buy_price']
        #print(buy_price, data['lowest_price'], (data['lowest_price'] - buy_price) / buy_price * 100 )

        if (data['lowest_price'] - buy_price) / buy_price * 100 <= -10:
            cut_count += 1
            report.append({'code': code, 'buy_price': buy_price, 'sell_price': data['lowest_price'],
                'set_date': code_dict[code]['setdate'], 'buy_date': code_dict[code]['buy_date'],
                'sell_date': today, 'profit': (data['lowest_price'] - buy_price) / buy_price * 100})
            #print('sell')
            code_dict[code]['state'] = STATE_NONE
            break
        elif (data['highest_price'] - buy_price) / buy_price * 100 >= 10:
            #print('good')
            meet_count += 1 
            report.append({'code': code, 'buy_price': buy_price, 'sell_price': data['lowest_price'],
                'set_date': code_dict[code]['setdate'], 'buy_date': code_dict[code]['buy_date'], 
                'sell_date': today, 'profit': (data['highest_price'] - buy_price) / buy_price * 100})
            code_dict[code]['state'] = STATE_NONE
            break

    return meet_count, cut_count


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    #market_code = ['A044960', 'A010660']
    #market_code = ['A010660']

    meet_count = 0
    cut_count = 0
    from_date = date(2018, 1, 1)
    until_date = date(2019, 10, 15)
    for code in market_code:
        code_dict[code] = {'state': STATE_UNKNOWN, 'data': None, 'data_list': None, 'today_bull': 0, 'mvg': 0,
                            'buy_date': None,
                            'buy_price': 0, 'amount': 0, 'set_date': None, 'highest': 0, 'last_bull_date': None}

    set_first_over_mavg(message_reader, market_code, from_date, until_date)
    while from_date <= until_date:
        if holidays.is_holidays(from_date):
            from_date += timedelta(days=1)
            continue
        start_today_trading(message_reader, market_code, from_date)
        meet, cut = evaluate_meet_goal(message_reader, from_date)
        cut_count += cut
        meet_count += meet
        #print(from_date, f"cut: {cut}, meet: {meet}, state:{code_dict['A010660']['state']}, bull:{code_dict['A010660']['today_bull']}, mvg:{code_dict['A010660']['mvg']}")
        #print(from_date, f"cut: {cut}, meet: {meet}, state:{code_dict['A044960']['state']}, bull:{code_dict['A044960']['today_bull']}, mvg:{code_dict['A044960']['mvg']}")
        print(from_date, f"cut: {cut}, meet: {meet}")
        from_date += timedelta(days=1)
    print('-' * 100)
    print('summary succeess', meet_count, 'cut:', cut_count)
    print('-' * 100)
    df = pd.DataFrame(report)
    df.to_excel('bull_over_120.xlsx')
