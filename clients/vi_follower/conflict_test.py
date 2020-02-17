from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))


from clients.common import morning_client
from datetime import datetime, date
from morning.back_data import holidays
from morning_server import stock_api
import gevent
from gevent.queue import Queue
from clients.vi_follower import stock_follower_conflict as stock_follower
from configs import db
from pymongo import MongoClient
from utils import time_converter


subscribe_code = dict()
yesterday_data = dict()
db_collection = None


def check_time():
    while True:
        gevent.sleep(60)


def start_vi_follower():
    global db_collection

    market_code = morning_client.get_market_code()
    today = datetime.now().date()
    #if holidays.is_holidays(today):
    #    print('today is holiday')
    #    sys.exit(1)

    yesterday = holidays.get_yesterday(today)
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    yesterday_list = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            yesterday_data[code] = data
            yesterday_list.append(data)
    print('')
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)

    yesterday_list = yesterday_list[:100]
    for ydata in yesterday_list:
        code = ydata['code']
        sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code, yesterday_data[code])
        sf.subscribe_at_startup()
        subscribe_code[code] = sf

    print('Start Listening...')

    time_check_thread = gevent.spawn(check_time)
    gevent.joinall([time_check_thread])


if __name__ == '__main__':
    start_vi_follower()
