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
from clients.vi_follower import stock_follower
from configs import db
from pymongo import MongoClient
from utils import time_converter


subscribe_code = dict()
yesterday_data = dict()
tasks = Queue()

def start_watch(db_client):
    while True:
        code = tasks.get()
        if code in subscribe_code:
            pass
        else:
            sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code, yesterday_data[code])
            if sf.start_watch():
                subscribe_code[code] = sf
            else:
                print('Failed to watch', code)


def vi_handler(_, data):
    print('ALARM', data)
    data = data[0]
    db_collection['alarm'].insert_one(data)
    if data['1'] == ord('1') and data['2'] == 201:
        alarm_time = data['0']
        code = data['3']
        print(data)
        if data['4'] == 755: # start
            tasks.put_nowait(code)
            print('put code', code)
        elif data['4'] == 756: # stop
            pass # Start monitoring


if __name__ == '__main__':
    market_code = morning_client.get_market_code()
    today = datetime.now().date()
    if holidays.is_holidays(today):
        print('today is holiday')
        sys.exit(1)

    yesterday = holidays.get_yesterday(today)
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    yesterday_list = []
    db_list = list(db_collection['amount_rank'].find({'0': time_converter.datetime_to_intdate(today)}))

    if len(db_list) > 0:
        yesterday_list = db_list
    else:
        for progress, code in enumerate(market_code):
            print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
            data = morning_client.get_past_day_data(code, yesterday, yesterday)
            if len(data) == 1:
                yesterday_data[code] = data[0]
                yesterday_list.append(data[0])
        print('')
        yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)

    yesterday_list = yesterday_list[:100]
    for ydata in yesterday_list:
        sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, ydata['code'], yesterday_data[code])
        sf.subscribe_at_startup()
        subscribe_code[code] = sf
        if len(db_list) == 0:
            db_collection['amount_rank'].insert_one(ydata)

    print('Start Listening...')
    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)

    gevent.spawn(start_watch, db_collection).join()
