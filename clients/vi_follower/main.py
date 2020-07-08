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


def today_bull_record():
    while True:
        now = datetime.now()
        if now.hour >= 16 and now.minute > 30:
            result = morning_client.get_past_day_data('A005930', date(now.month, now.day), date(now.month, now.day))
            if len(result) == 1:
                break

    now = datetime.now()
    now_date = now.year * 10000 + now.month * 100 + now.day
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm
    tdata = list(db_collection['yamount'].find({'date': now_date}))
    if len(tdata) == 0:
        market_code = morning_client.get_all_market_code()
        today_list = get_day_data(now, market_code)
        today_list = sorted(today_list, key=lambda x: x['amount'], reverse=True)
        today_list = today_list[:1000]
        codes = [c['code'] for c in today_list]
        db_collection['yamount'].insert_one({'date': now_date, 'codes': codes})


def get_day_data(query_date, market_code):
    result = []
    for progress, code in enumerate(market_code):
        print('collect yesterday data', f'{progress+1}/{len(market_code)}', end='\r')
        data = morning_client.get_past_day_data(code, yesterday, yesterday)
        if len(data) == 1:
            data = data[0]
            data['code'] = code
            result.append(data)
    print('')
    return result


def start_vi_follower():
    global db_collection

    slack.send_slack_message('START VI FOLLOWER')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    market_code = morning_client.get_all_market_code()
    for m in market_code: # for caching company name in server
        morning_client.code_to_name(m)

    yesterday = holidays.get_yesterday(datetime.now())
    yesterday_date = yesterday.year * 10000 + yesterday.month * 100 + yesterday.day
    ydata = list(db_collection['yamount'].find({'date': yesterday_date}))

    if len(ydata) == 0:
        yesterday_list = get_day_data(yesterday, market_code)
        yesterday_list = sorted(yesterday_list, key=lambda x: x['amount'], reverse=True)
        yesterday_list = yesterday_list[:1000]
        codes = [c['code'] for c in yesterday_list]
        db_collection['yamount'].insert_one({'date': yesterday_list[0]['0'], 'codes': codes})
    else:
        codes = ydata[0]['codes']

    if len(codes) == 0:
        print('Critical Error, No CODES')
        sys.exit(0)

    followers = []
    for code in codes:
        sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code)
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
    today_bull_record_thread = gevent.spawn(today_bull_record)
    gevent.joinall([time_check_thread, today_bull_record])


if __name__ == '__main__':
    start_vi_follower()
