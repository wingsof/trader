"""
    1. search past data and set status of each code
    2. get long list and set status of each code status
    3. start subscribe for selected codes
    4. Do trades according to rules
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
from configs import db
from clients.mavg_trader import today_watcher, trade_account, trader_env


class CodeInfo:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def convert_data_readable(code, past_data):
    converted_data = []
    avg_prices = np.array([])
    avg_volumes = np.array([])
    for p in past_data:
        converted = dt.cybos_stock_day_tick_convert(p)
        converted['code'] = code
        avg_prices = np.append(avg_prices, np.array([converted['close_price']]))
        avg_volumes = np.append(avg_volumes, np.array([converted['volume']]))

        if len(avg_prices) == trader_env.MAVG:
            converted['moving_average'] = avg_prices.mean()
            avg_prices = avg_prices[1:]
            converted['volume_average'] = avg_volumes.mean()
            avg_volumes = avg_volumes[1:]
        else:
            converted['moving_average'] = 0
            converted['avg_volumes'] = 0

        converted_data.append(converted)

    return converted_data


def get_past_data(reader, code, from_date, until_date):
    past_data = stock_api.request_stock_day_data(reader, code, from_date, until_date)
    if trader_env.MAVG * 2 * 0.6 > len(past_data):
        #print('PAST DATA too short', len(past_data), code)
        return []
    elif past_data[-1]['0'] != time_converter.datetime_to_intdate(until_date):
        #print(code, until_date, 'Cannot get last day data')
        return []
    return past_data


def find_first_cross_data(past_data):
    # search from yesterday, i should be greater than 0 since already checked yesterday data which over mavg
    over_datas = []
    not_over = None
    for p in past_data:
        if p['moving_average'] < p['close_price']:
            over_datas.insert(0, p)
        else:
            not_over = p
            break
    return not_over, over_datas


def find_highest(past_data):
    index = -1
    price = 0

    for i, d in enumerate(past_data):
        if d['highest_price'] > price:
            index = i
            price = d['highest_price']

    return index


def get_long_list(reader, code_dict, today):
    if not trader_env.RUNNING_SIMULATION: 
        # list of dict {code, name, quantity, sell_available, price, all_price} price is buy price
        long_list = stock_api.request_long_list(reader)
        print('LONG LIST', len(long_list))
        for l in long_list:
            print('LONG', l['code'], l['price'], l['sell_available'])
            code_dict[l['code']] = CodeInfo(state=trader_env.STATE_LONG, buy_price=l['price'], sell_available=l['sell_available'], yesterday_data=None, today_date=today, cut=0)
    else:
        for k, v in trade_account.TradeAccount.GetAccount().get_long_list().items():
            code_dict[k] = CodeInfo(state=trader_env.STATE_LONG, buy_price=v['price'], sell_available=v['sell_available'], yesterday_data=None, today_date=today, cut=0)


def start_today_trading(reader, market_code, today):
    code_dict = dict()

    # starting point for the loop of simulation
    yesterday = holidays.get_yesterday(today)
    get_long_list(reader, code_dict, today)

    candidate_over_avg = []
    for progress, code in enumerate(market_code):
        print('over avg', today, f'{progress+1}/{len(market_code)}', end='\r')
        past_data = get_past_data(reader, code, yesterday - timedelta(days=trader_env.MAVG*3), yesterday)
        if len(past_data) == 0:
            continue
        past_data = convert_data_readable(code, past_data)
        yesterday_data = past_data[-1]

        if code in code_dict:
            code_dict[code].yesterday_data = yesterday_data
            #print(yesterday_data['moving_average'], yesterday_data['close_price']) 
            continue
        if yesterday_data['moving_average'] < yesterday_data['close_price']:
            candidate_over_avg.append(code)
            code_dict[code] = CodeInfo(state=trader_env.STATE_NONE, buy_price=0, sell_available=0,
                                        yesterday_data=yesterday_data, past_data=None, cut=0,
                                        from_highest=0, average_amount=0, buy_date_profit=0,
                                        cross_data=None, before_cross_data=None, mavg_data=past_data)
    print('')
    candidate_cross_data = []
    for progress, code in enumerate(candidate_over_avg):
        not_cross, cross_data = find_first_cross_data(code_dict[code].mavg_data[-1::-1])
        if 2 <= len(cross_data) <= 7:
            increase_candle = cross_data[0]['start_price'] < cross_data[0]['close_price'] and cross_data[1]['start_price'] < cross_data[1]['close_price'] 
            if increase_candle:
                code_dict[code].cross_data = cross_data
                code_dict[code].before_cross_data = not_cross
                code_dict[code].cut = max([cross_data[0]['highest_price'], cross_data[1]['highest_price']])
                candidate_cross_data.append(code)


    for progress, code in enumerate(candidate_cross_data):
        #print('get past data', today, f'{progress+1}/{len(candidate_cross_data)}', end='\r')
        past_data = get_past_data(reader, code, yesterday - timedelta(days=365), yesterday) 
        if len(past_data) == 0:
            continue
        past_data_c = convert_data_readable(code, past_data)
        
        code_dict[code].past_data = past_data_c
    #print('\nget past data done')


    highest_check_data = []
    for progress, code in enumerate(candidate_cross_data):
        days_from_highest = find_highest(code_dict[code].past_data[-1::-1])
        #print(days_from_highest, len(code_dict[code].cross_data))
        if days_from_highest < len(code_dict[code].cross_data):
            days_from_highest = 0

        amount_array = [code_dict[code].cross_data[0]['amount'], code_dict[code].cross_data[1]['amount']]
        average_amount = np.array(amount_array).mean()
        code_dict[code].from_highest = days_from_highest
        code_dict[code].average_amount = average_amount
        if days_from_highest != 0:
            if ((days_from_highest <= 15 and average_amount >  200000000) or
                    (days_from_highest >= 200 and average_amount < 360000000)):
                highest_check_data.append(code)

        #print(days_from_highest, average_amount)


    over_profit_check_data = []
    for progress, code in enumerate(highest_check_data):
        over_profit_array = [code_dict[code].before_cross_data['close_price'], code_dict[code].cross_data[0]['close_price'], code_dict[code].cross_data[1]['close_price']]
        if ((over_profit_array[2] - over_profit_array[1]) / over_profit_array[1] * 100 < 20 and
                (over_profit_array[1] - over_profit_array[0]) / over_profit_array[0]  * 100 < 20):
            over_profit_check_data.append(code)

    over_days_profit_check_data = []
    for progress, code in enumerate(over_profit_check_data):
        cross_data = code_dict[code].cross_data
        passed = True
        for i in range(2, len(cross_data)):
            if (cross_data[i]['highest_price'] - cross_data[i-1]['close_price']) / cross_data[i-1]['close_price'] * 100 >= 10:
                passed = False
                break

        if passed:
            over_days_profit_check_data.append(code)
            for i in range(2, len(cross_data)):
                if cross_data[i]['close_price'] < cross_data[i-1]['close_price']:
                    if cross_data[i]['highest_price'] > code_dict[code].cut:
                        code_dict[code].cut = cross_data[i]['highest_price']

    print(today, 'over avg', len(candidate_over_avg), '\tcross over', len(candidate_cross_data), '\thighest', len(highest_check_data), '\tover profit', len(over_profit_check_data), '\tover days', len(over_days_profit_check_data))
    for code in over_days_profit_check_data:
        code_dict[code].state = trader_env.STATE_OVER_AVG

    for k, v in code_dict.items():
        if v.state != trader_env.STATE_NONE:
            today_watcher.add_watcher(reader, k, v, today, v.state, trader_env.RUNNING_SIMULATION)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (message.SERVER_IP, message.CLIENT_SOCKET_PORT)
    sock.connect(server_address)
    message_reader = stream_readwriter.MessageReader(sock)
    message_reader.start()
    market_code = stock_api.request_stock_code(message_reader, message.KOSDAQ)
    if trader_env.RUNNING_SIMULATION:
        # if running simulation then account should be simulation mode regardless of account mode
        if len(trader_env.CODES) > 0:
            market_code = trader_env.CODES
        trade_account.TRADE_SIMULATION = True

    trade_account.TradeAccount.GetAccount(message_reader)
    if trader_env.RUNNING_SIMULATION:
        from_date = trader_env.RUNNING_FROM
        until_date = trader_env.RUNNING_UNTIL
        while from_date <= until_date:
            if holidays.is_holidays(from_date):
                from_date += timedelta(days=1)
                continue
            start_today_trading(message_reader, market_code, from_date)

            today_watcher.today_traders.clear()
            from_date += timedelta(days=1)
    else:
        today = datetime.now().date()
        start_today_trading(message_reader, market_code, today)
        message_reader.join()

    if trader_env.RUNNING_SIMULATION:
        import pandas as pd
        df = pd.DataFrame(trade_account.TradeAccount.GetAccount().get_trade_list())
        df.to_excel('mavg_trader.xlsx')
