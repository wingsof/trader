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

db_collection = None


def vi_handler(_, data):
    print('ALARM', data)
    data = data[0]
    db_collection['alarm'].insert_one(data)


def check_time():
    while True:
        now = datetime.now()
        if now.hour >= 18 and now.minute >= 35:
            break
        gevent.sleep(60)


def start_vi_follower():
    global db_collection

    slack.send_slack_message('START VI FOLLOWER')
    db_collection = MongoClient(db.HOME_MONGO_ADDRESS).trade_alarm

    market_code = []
    kosdaq_code = morning_client.get_market_code()
    kospi_code = morning_client.get_market_code(message.KOSPI)
    market_code.extend(kosdaq_code)
    market_code.extend(kospi_code)

    market_code = list(dict.fromkeys(market_code))

    followers = []
    for code in market_code:
        sf = stock_follower.StockFollower(morning_client.get_reader(), db_collection, code)
        sf.subscribe_at_startup()
        followers.append(sf)

    print('Start Listening...')
    slack.send_slack_message('START LISTENING')
    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)

    time_check_thread = gevent.spawn(check_time)
    gevent.joinall([time_check_thread])
    slack.send_slack_message('VI FOLLOWER DONE')


if __name__ == '__main__':
    start_vi_follower()
