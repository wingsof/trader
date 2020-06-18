from gevent import monkey
monkey.patch_all()

import gevent

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 1))))

from concurrent import futures

from datetime import datetime, timedelta
from clients.common import morning_client
from morning.back_data import holidays
from pymongo import MongoClient
from morning_server import stock_api
from gevent.queue import Queue


# check_mongo_performance.py "2020/03/25 09:02" took  0:00:24.764038
# load done tick len 48742 real time 2020-06-04 14:49:45.223657  took 0:00:08.916987, just have 2020/3/11 data in db, it is much faster
# test1: copy 1 more days to mongodb and re-measure time (3/12)
#   * load done tick len 48742 real time 2020-06-04 15:58:00.676326  took 0:00:31.452220
# test2: set date as index and measure time
#   * load done tick len 48742 real time 2020-06-04 16:06:12.708876  took 0:00:03.753992
# test3: create 1 day data and set date as index and test performance
#   * not set as index: load done tick len 52026 real time 2020-06-04 17:20:09.219083  took 0:00:06.708520
#   * set as index: load done tick len 52026 real time 2020-06-04 17:23:52.252392  took 0:00:00.522798



def get_yesterday_data(today, market_code):
    yesterday = holidays.get_yesterday(today)
    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_list.append(data)
    print('')
    return yesterday_list


def collect_db(code, db_collection, from_time, until_time):
    datas = []
    tick_data = list(db_collection[code].find({'date': {'$gt': from_time, '$lte': until_time}}))
    for t in tick_data:
        t['code'] = code
    ba_data = list(db_collection[code+'_BA'].find({'date': {'$gt': from_time, '$lte': until_time}}))

    for bd in ba_data:
        bd['code'] = code

    subject_data = list(db_collection[code+'_S'].find({'date': {'$gt': from_time, '$lte': until_time}}))
    for sd in subject_data:
        sd['code'] = code

    datas.extend(tick_data)
    datas.extend(ba_data)
    datas.extend(subject_data)
    return datas


def start_tick_provider(simulation_datetime):
    AT_ONCE_SECONDS = 60
    tick_queue = Queue()
    db_collection = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
    market_code = morning_client.get_all_market_code()
    print('market_code len', len(market_code))
    all_data = []
    yesterday_list = get_yesterday_data(simulation_datetime, market_code)
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:1000]
    market_codes = [yl['code'] for yl in yesterday_list]

    load_start_time = datetime.now()
    print('load data', simulation_datetime, 'real time', load_start_time)
    for progress, code in enumerate(market_codes):
        all_data.extend(collect_db(code, db_collection, simulation_datetime, simulation_datetime + timedelta(seconds=AT_ONCE_SECONDS)))
        print('collect tick data', f'{progress+1}/{len(market_codes)}', end='\r')
    print('')
    load_finish_time = datetime.now()
    all_data = sorted(all_data, key=lambda x: x['date'])
    print('load done', 'tick len', len(all_data), 'real time', load_finish_time, ' took', load_finish_time - load_start_time)


def start_tick_provider2(simulation_datetime):
    AT_ONCE_SECONDS = 60
    tick_queue = Queue()
    db_collection = MongoClient('mongodb://127.0.0.1:27017').trade_alarm
    all_data = []

    load_start_time = datetime.now()
    print('load data', simulation_datetime, 'real time', load_start_time)
    time_str = 'T' + simulation_datetime.strftime('%Y%m%d')
    datas = list(db_collection[time_str].find({'date': {'$gt': simulation_datetime, '$lte': simulation_datetime + timedelta(seconds=AT_ONCE_SECONDS)}}))
    datas = sorted(datas, key=lambda x: x['date'])
    load_finish_time = datetime.now()
    print('load done', 'tick len', len(datas), 'real time', load_finish_time, ' took', load_finish_time - load_start_time)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage:', sys.argv[0], 'datetime(2019/9/2 11:52)')
    else:
        simulation_datetime = datetime.strptime(sys.argv[1], '%Y/%m/%d %H:%M')
        start_tick_provider2(simulation_datetime)

