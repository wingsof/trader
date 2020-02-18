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
from utils import slack
from configs import time_info


subscribe_code = dict()
yesterday_data = dict()
db_collection = None
tasks = Queue()

def start_watch():
    while True:
        msg = tasks.get().split(':')

        if msg[0] == 'alarm':
            code = msg[1]
            if code in subscribe_code:
                pass
            else:
                if code in yesterday_data:
                    sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code, yesterday_data[code])
                else:
                    sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code, None)
                if sf.start_watch():
                    subscribe_code[code] = sf
                else:
                    print('Failed to watch', code)
        elif msg[0] == 'exit':
            break


def vi_handler(_, data):
    print('ALARM', data)
    data = data[0]
    db_collection['alarm'].insert_one(data)
    if data['1'] == ord('1') and data['2'] == 201:
        alarm_time = data['0']
        code = data['3']
        print(data)
        if data['4'] == 755: # start
            tasks.put_nowait('alarm:' + code)
            print('put code', code)
        elif data['4'] == 756: # stop
            tasks.put_nowait('disalarm:' + code)


def check_time():
    while True:
        now = datetime.now()
        if now.hour >= 18 and now.minute >= 35:
            tasks.put_nowait('exit:')
            break
        gevent.sleep(60)


def start_vi_follower():
    global db_collection

    slack.send_slack_message('START VI FOLLOWER')
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
    slack.send_slack_message('START LISTENING')
    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)

    watch_thread = gevent.spawn(start_watch)
    time_check_thread = gevent.spawn(check_time)
    gevent.joinall([watch_thread, time_check_thread])
    slack.send_slack_message('VI FOLLOWER DONE')

if __name__ == '__main__':
    start_vi_follower()
