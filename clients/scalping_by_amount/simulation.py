from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
from configs import client_info
client_info.TEST_MODE = True
from gevent.queue import Queue

import gevent
from pymongo import MongoClient
from datetime import timedelta

from clients.scalping_by_amount.mock import stock_api
from clients.scalping_by_amount.mock import datetime
from clients.common import morning_client
from datetime import datetime as rdatetime
from clients.scalping_by_amount import main
from configs import db


ready_queue = gevent.queue.Queue()


datetime.current_datetime = rdatetime(2020, 3, 16, 8, 55)
finish_time = rdatetime(2020, 3, 16, 15, 35)

stock_api.balance = 10000000


def collect_db(code, db_collection, from_time, until_time):
    datas = []
    tick_data = list(db_collection[code].find({'date': {'$gte': from_time, '$lte': until_time}}))
    for t in tick_data:
        t['code'] = code
    ba_data = list(db_collection[code+'_BA'].find({'date': {'$gte': from_time, '$lte': until_time}}))

    for bd in ba_data:
        bd['code'] = code
    datas.extend(tick_data)
    datas.extend(ba_data)
    return datas


def start_provide_tick():
    db_collection = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
    market_codes = ready_queue.get()
    print('start_provide_tick', datetime.current_datetime, finish_time)

    while datetime.now() < finish_time:
        all_data = []
        start_time = datetime.now()
        until_time = datetime.now() + timedelta(seconds=60)
        for code in market_codes:
            #print('collect tick', code, f"{progress}/{len(market_codes)}")
            all_data.extend(collect_db(code, db_collection, start_time, until_time))

        all_data = sorted(all_data, key=lambda x: x['date']) 

        for tick in all_data:
            datetime.current_datetime = tick['date']

            if '68' in tick:
                stock_api.send_bidask_data(tick['code'], tick)
                stock_api.set_current_first_bid(tick['code'], tick['4'])
            else:
                stock_api.send_tick_data(tick['code'], tick)
            gevent.sleep()
        if datetime.now() == start_time:
            datetime.current_datetime += timedelta(seconds=60)

        print('progressing', datetime.now(), 'handle', len(all_data), 'ticks')


tick_thread = gevent.spawn(start_provide_tick)
main.start_trader(ready_queue)

gevent.joinall([tick_thread])
