from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from utils import trade_logger as logger
from clients.common import morning_client
from datetime import timedelta
from morning.back_data import holidays
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import datetime
else:
    from datetime import datetime

from morning_server import message
import gevent
from gevent.queue import Queue
from clients.scalping_by_amount import stock_follower
from clients.scalping_by_amount import pickstock_experiment as pickstock
from clients.scalping_by_amount import time
import pandas as pd
import numpy as np
from pymongo import MongoClient


db_collection = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
followers = []
DELTA = 0
PICK_SEC = 1
MINIMUM_AMOUNT = 100000000
candidate_queue = gevent.queue.Queue()
results = []


def search_profit(code, start_time, amount, pick_profit, max_min_volume, buy_volume, sell_volume, buy_speed, sell_speed):
    tick_data = list(db_collection[code].find({'date': {'$gte': start_time, '$lte': start_time + timedelta(seconds=300)}}))
    if len(tick_data) == 0:
        print('ERROR no tick data')

    price_arr = np.array([d['13'] for d in tick_data])
    
    p = price_arr[0]
    highest = np.amax(price_arr)
    lowest = np.amin(price_arr)

    highest_index = -1
    lowest_index = -1 
    for i, price in enumerate(price_arr):
        if price == highest and highest_index == -1:
            highest_index = i
        if price == lowest and lowest_index == -1:
            lowest_index = i

        if highest_index >= 0 and lowest_index >= 0:
            break

    price_std = np.std((price_arr - p) / p * 100.)
    mean = np.mean(price_arr)
    highest_profit = (highest - p) / p * 100.
    lowest_profit = (lowest - p) / p * 100.
    mean_profit = (mean - p) / p * 100.
    results.append({'time': start_time,
                    'code': code,
                    'tick_len': len(tick_data),
                    'highest_profit': highest_profit,
                    'lowest_profit': lowest_profit,
                    'highest_arrive_time': (tick_data[highest_index]['date'] - tick_data[0]['date']).total_seconds(),
                    'lowest_arrive_time': (tick_data[lowest_index]['date'] - tick_data[0]['date']).total_seconds(),
                    'mean_profit': mean_profit,
                    'amount': amount,
                    'pick_profit': pick_profit,
                    'profit_std': price_std,
                    'past_max_min_volume': max_min_volume,
                    'buy_volume': buy_volume,
                    'sell_volume': sell_volume,
                    'buy_speed': buy_speed,
                    'sell_speed': sell_speed})


def data_process():
    picker = pickstock.PickStock()
    now = datetime.now()
    start_time = now.replace(hour=9+DELTA, minute=0, second=3)
    done_time = now.replace(hour=15+DELTA, minute=10, second=0)
    pick_finish_time = now.replace(hour=15+DELTA, minute=5, second=0)
    entered = False
    last_processed_time = datetime.now()

    while True:
        if start_time <= datetime.now() <= done_time:
            entered = True

            while datetime.now() - last_processed_time < timedelta(seconds=PICK_SEC):
                gevent.sleep()

            candidates = []
            print(datetime.now(), 'RUN PICKER')
            for sf in followers:
                snapshot = sf.snapshot(PICK_SEC)
                if (snapshot is None or
                    not sf.is_in_market() or
                    snapshot['profit'] < 0.5 or
                    snapshot['yesterday_close'] == 0 or
                    snapshot['today_open'] == 0 or
                    snapshot['minute_max_volume'] / (15/PICK_SEC) > snapshot['buy_volume'] + snapshot['sell_volume'] or
                    snapshot['today_open'] < snapshot['yesterday_close'] or
                    snapshot['amount'] < MINIMUM_AMOUNT):
                    continue
                candidates.append(snapshot)
            picked = picker.pick_one(candidates)
            if picked is not None and datetime.now() <= pick_finish_time:
                search_profit(picked['code'], datetime.now(), picked['amount'], picked['profit'], picked['minute_max_volume'], picked['buy_volume'], picked['sell_volume'], picked['buy_speed'], picked['sell_speed'])
                logger.info('PICKED %s, amount: %d, profit: %f', picked['code'], picked['amount'],
                            picked['profit'])
            last_processed_time = datetime.now()
        else:
            if entered:
                logger.info('QUEUE EXIT')
                date_str = datetime.now().strftime('%Y%m%d')
                pd.DataFrame(results).to_excel('picker_' + date_str + '_' + str(PICK_SEC) + '.xlsx')
                candidate_queue.put_nowait({'code': 'exit', 'info': None})
                entered = False
                break
        gevent.sleep(0.02)


def heart_beat():
    last_processed_time = datetime.now()
    finish_flag = False
    while True:
        while datetime.now() - last_processed_time < timedelta(seconds=1):
            gevent.sleep()
        candidates = []
        while not candidate_queue.empty():
            candidates.append(candidate_queue.get())

        #print('candidate size', len(candidates), datetime.now())
        for c in candidates:
            if c['code'] == 'exit':
                logger.warning('SET FINISH FLAG')
                finish_flag = True

        if finish_flag:
            logger.warning('FINISH TODAY WORK')
            break
        else:
            for fw in followers:
                if fw.is_in_market():
                    fw.process_tick()

        last_processed_time = datetime.now()


def get_yesterday_data(today, market_code):
    yesterday = holidays.get_yesterday(today)
    one_week_before= holidays.get_date_by_previous_working_day_count(today, 5)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            min_data = morning_client.get_minute_data(code, one_week_before, yesterday)
            if len(min_data) > 0:
                data['minute_max_volume'] = max([d['volume'] for d in min_data])
            else:
                data['minute_max_volume'] = 0

            yesterday_list.append(data)
    print('')
    return yesterday_list


def start_trader(ready_queue=None):
    print('start trader', datetime.now())
    market_code = []
    kosdaq_code = morning_client.get_market_code()
    kospi_code = morning_client.get_market_code(message.KOSPI)
    market_code.extend(kosdaq_code)
    market_code.extend(kospi_code)

    market_code = list(dict.fromkeys(market_code))
    market_code =  list(filter(lambda x: len(x) > 0 and x[1:].isdigit(), market_code))
    yesterday_list = get_yesterday_data(datetime.now(), market_code) 
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:1000]

    for yesterday_data in yesterday_list:
        code = yesterday_data['code']
        sf = stock_follower.StockFollower(morning_client.get_reader(), code, yesterday_data, code in kospi_code)
        sf.subscribe_at_startup()
        followers.append(sf)

    if ready_queue is not None:
        ready_queue.put_nowait([yl['code'] for yl in yesterday_list])
    gevent.joinall([gevent.spawn(heart_beat), gevent.spawn(data_process)])


if __name__ == '__main__':
    search_profit('A005930', datetime(2020, 3, 12, 9, 5), 1000000, 1.0)
    print(results)