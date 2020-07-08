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
from clients.vi_follower import stock_follower
from configs import db
from pymongo import MongoClient
from utils import time_converter
from utils import slack
from configs import time_info

db_collection = None


def vi_handler(_, data):
    print('ALARM', data)
    data = data[0]
    db_collection['alarm'].insert_one(data)


def check_time():
    while True:
        now = datetime.now()
        if now.hour >= 18 and now.minute >= 35:
            slack.send_slack_message('VI FOLLOWER DONE')
            sys.exit(0)
        gevent.sleep(60)


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


def start_vi_follower():
    global db_collection

    slack.send_slack_message('START VI FOLLOWER')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    market_code = morning_client.get_all_market_code()
    for m in market_code: # for caching company name in server
        morning_client.code_to_name(m)

    yesterday_list = get_yesterday_data(datetime.now(), market_code)
    yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
    yesterday_list = yesterday_list[:1000]
    codes = [c['code'] for c in yesterday_list]

    if len(codes) == 0:
        print('Critical Error, No CODES')
        sys.exit(0)

    ydata = list(db_collection['yamount'].find({'date': yesterday_list[0]['0']}))
    if len(ydata) == 0:
        db_collection['yamount'].insert_one({'date': yesterday_list[0]['0'], 'codes': codes})

    followers = []
    for yesterday_data in yesterday_list:
        sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, yesterday_data['code'])
        sf.subscribe_at_startup()
        followers.append(sf)

    kosdaq_index = stock_follower.StockFollower(morning_client.get_reader(), db_collection, 'U201')
    kosdaq_index.subscribe_at_startup()
    followers.append(kosdaq_index)

    kospi_index = stock_follower.StockFollower(morning_client.get_reader(), db_collection, 'U001')
    kospi_index.subscribe_at_startup()
    followers.append(kospi_index)

    print('Start Listening...')
    slack.send_slack_message('START LISTENING')
    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)

    time_check_thread = gevent.spawn(check_time)
    gevent.joinall([time_check_thread])


if __name__ == '__main__':
    start_vi_follower()
