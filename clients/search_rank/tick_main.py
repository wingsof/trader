from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences
import pandas as pd


def filter_in_market_tick(tick_data):
    index = 0
    for i, d in enumerate(tick_data):
        if d['market_type'] == dt.MarketType.IN_MARKET:
            index = i
            break
    return tick_data[index]['current_price'], tick_data[index+1:]


def print_rank_code(code, sec_delta, search_time, rank_by_profit, rank_by_amount):
    for i, rbp in enumerate(rank_by_profit):
        if rbp['code'] == code:
            print('RANK BY PROFIT', 'code', code, 'delta', sec_delta, 'search time', search_time, 'from open', "{0:.2f}".format(rbp['from_open']), 'profit', "{0:.2f}".format(rbp['profit']), 'RANK', i+1)
            break

    for i, rba in enumerate(rank_by_amount):
        if rba['code'] == code:
            print('RANK BY AMOUNT', 'code', code, 'delta', sec_delta, 'search time', search_time, 'from open', "{0:.2f}".format(rba['from_open']), 'amount', rba['amount'], 'RANK', i+1)
            break


def get_open_price(code, search_time, db_collection):
    open_tick_data = list(db_collection[code].find({'date': {'$gte': datetime.combine(search_time.date(), time(8,58)), '$lte': datetime.combine(search_time.date(), time(9,5))}}))
    if len(open_tick_data) == 0:
        #print('no open tick data', code)
        return 0
    converted_data = []
    for td in open_tick_data:
        converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    open_price, _ = filter_in_market_tick(converted_data)
    return open_price


def start_search(code, search_time, yesterday_list, price, qty, db_collection):
    print('start_search')
    code_dict = dict()
    no_open_price_count = 0
    for progress, data in enumerate(yesterday_list):
        ycode = data['code']
        open_price = get_open_price(ycode, search_time, db_collection)
        if open_price == 0:
            #print('cannot get open price', ycode)
            if ycode == code:
                print(code, 'cannot get open price')
                sys.exit(1)
            no_open_price_count += 1
            print('get tick info', f'{progress+1-no_open_price_count}/{no_open_price_count}/{len(yesterday_list)}', end='\r')
            continue
        print('get tick info', f'{progress+1-no_open_price_count}/{no_open_price_count}/{len(yesterday_list)}', end='\r')
        # ex) 9:02 -> then find from 9:01 <= time < 9:03
        tick_data = list(db_collection[ycode].find({'date': {'$gte': search_time - timedelta(seconds=60), '$lt': search_time + timedelta(seconds=60)}}))
        converted_data = []
        for td in tick_data:
            converted = dt.cybos_stock_tick_convert(td)
            converted_data.append(converted)

        if (search_time.hour == 9 and search_time.minute < 2) or search_time.hour < 9:
            converted_data = filter_in_market_tick(converted_data)

        code_dict[ycode] = {'tick': converted_data, 'yesterday_data': data, 'open': open_price}
        # loop ex) 9:02 -> from 9:02:00 to 9:02:59  loop by increment 1 second and search past 10 sec, 20 sec, 30 sec, 40 sec, 50 sec, 60 sec
   
    print('')
    until_time = search_time + timedelta(seconds=60) 

    if code not in code_dict:
        print(code, 'not in code_dict')
        sys.exit(1)

    time_price_match = []
    last_time = None
    target_code_tick = list(filter(lambda x: search_time <= x['date'] < until_time, code_dict[code]['tick']))
    for tc in target_code_tick:
        if tc['current_price'] == price and tc['volume'] == qty:
            time_price_match.append(tc['date'].replace(microsecond=0))
    time_price_match = list(dict.fromkeys(time_price_match))
    print('matched time', time_price_match)

    while search_time < until_time:
        if not search_time in time_price_match:
            search_time += timedelta(seconds=1)
            continue

        for t in range(60, 0, -10):
            rank_list = []
            for k, v in code_dict.items():
                tick = code_dict[k]['tick']
                tick = list(filter(lambda x: search_time - timedelta(seconds=t) <= x['date'] < search_time, tick))
                if len(tick) == 0:
                    continue
                profit = (tick[-1]['current_price'] - tick[0]['current_price']) / tick[0]['current_price'] * 100
                amount = sum([d['current_price'] * d['volume'] for d in tick])
                open_price = code_dict[k]['open']
                from_open = (tick[-1]['current_price'] - open_price) / open_price * 100
                rank_list.append({'code': k, 'profit': profit, 'amount': amount, 'from_open': from_open})

            rank_by_profit = sorted(rank_list, key=lambda x: x['profit'], reverse=True)
            rank_by_amount = sorted(rank_list, key=lambda x: x['amount'], reverse=True)
            print_rank_code(code, t, search_time, rank_by_profit, rank_by_amount)
            print('-' * 100)
            for rbp in rank_by_profit[:10]:
                print(rbp)
            print('*' * 100)
            for rba in rank_by_amount[:10]:
                print(rba)
            print('-' * 100)
                
        search_time += timedelta(seconds=1)


def get_tick_data(code, today, db_collection):
    from_datetime = datetime.combine(today, time(0,0))
    until_datetime = datetime.combine(today + timedelta(days=1), time(0,0))
    data = list(db_collection[code].find({'date': {'$gte': from_datetime, '$lte': until_datetime}}))
    converted_data = []
    for td in data:
        if code.endswith(message.BIDASK_SUFFIX):
            converted = dt.cybos_stock_ba_tick_convert(td)
        else:
            converted = dt.cybos_stock_tick_convert(td)
        converted_data.append(converted)
    return converted_data


if __name__ == '__main__':
    if len(sys.argv) < 5:
        print(sys.argv[0], 'code', 'time(2020-02-03 09:00)', 'price', 'qty')
        sys.exit(1)

    target_code = sys.argv[1]
    search_time = sys.argv[2]
    price = int(sys.argv[3])
    qty = int(sys.argv[4])

    # 나노메딕스, 2020/02/26 14:29
    # 미코, 2020/02/26 14:48
    search_time = datetime.strptime(search_time, '%Y-%m-%d %H:%M')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    tick_data = get_tick_data(target_code, search_time.date(), db_collection)

    if len(tick_data) == 0:
        print('No Tick Data for', target_code, search_time.date())
        sys.exit(1)

    print('Tick Data len', len(tick_data), tick_data[0])
    market_code = morning_client.get_market_code()
    yesterday = holidays.get_yesterday(search_time.date())
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:300]

    if len(tick_data) > 0:
        start_search(target_code, search_time, yesterday_list, price, qty, db_collection)
    else:
        print('Cannot find tick data')
