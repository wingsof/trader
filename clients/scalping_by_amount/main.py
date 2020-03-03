from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date
from morning.back_data import holidays
from morning_server import stock_api
from morning_server import message
import gevent
from gevent.queue import Queue
from clients.scalping_by_amount import stock_follower
from clients.scalping_by_amount import pickstock
from configs import db
from pymongo import MongoClient
from utils import time_converter
from configs import time_info


followers = []
DELTA = 0
MINIMUM_AMOUNT = 10000000
candidate_queue = gevent.queue.Queue()

def vi_handler(_, data):
    data = data[0]


def data_process():
    picker = pickstock.PickStock()
    now = datetime.now()
    start_time = now.replace(hour=9+DELTA, minute=0, second=3)
    done_time = now.replace(hour=15+DELTA, minute=10, second=0)

    while True:
        if start_time <= datetime.now() <= done_time:
            candidates = []
            for sf in followers:
                snapshot = sf.snapshot(10)
                if (snapshot is None or
                    snapshot['profit'] < 0 or
                    snapshot['yesterday_close'] == 0 or
                    snapshot['today_open'] == 0 or
                    snapshot['amount'] < MINIMUM_AMOUNT):
                    continue
                candidates.append(snapshot)
            code = picker.pick_one(candidates)
            if len(code) > 0:
                candidate_queue.put_nowait({'code': code, 'info': snapshot.copy()})
            gevent.sleep(10)


def heart_beat():
    last_processed_time = datetime.now()
    trading_follower = None
    while True:
        while datetime.now() - last_processed_time < timedelta(seconds=1):
            gevent.sleep(0.05)

        picked_code = None
        if trading_follower is None:
            while not candidate_queue.empty():
                picked_code = candidate_queue.get()

        last_processed_time = datetime.now()
        for fw in followers:
            fw.process_tick()
            if picked_code is not None and fw.code == picked_code['code']:
                trading_follower = fw
                fw.start_trading(picked_code['info'])

        if trading_follower is not None:
            if trading_follower.is_trading_done():
                trading_follower = None


def get_yesterday_data(today, market_code):
    yesterday = holidays.get_yesterday(today)
    yesterday_dict = dict()
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            yesterday_dict[code] = data
    print('')
    return yesterday_dict


def start_trader():
    market_code = []
    kosdaq_code = morning_client.get_market_code()
    kospi_code = morning_client.get_market_code(message.KOSPI)
    market_code.extend(kosdaq_code)
    market_code.extend(kospi_code)

    market_code = list(dict.fromkeys(market_code))
    market_code =  list(filter(lambda x: len(x) > 0 and x[1:].isdigit(), market_code))
    yesterday_data = get_yesterday(datetime.now(), market_code) 

    for code in market_code:
        yesterday_summary = None
        if code in yesterday_data:
            yesterday_summary = yesterday_data[code]
        sf = stock_follower.StockFollower(morning_client.get_reader(), code, yesterday_summary, code in kospi_code)
        sf.subscribe_at_startup()
        followers.append(sf)

    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)
    stock_api.subscribe_trade(morning_client.get_reader(), receive_result)

    gevent.joinall([gevent.spawn(heart_beat), gevent.spawn(data_process)])


if __name__ == '__main__':
    start_trader()
