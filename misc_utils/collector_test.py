from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from clients.common import morning_client
from datetime import datetime, date
from morning.back_data import holidays
from morning_server import stock_api
from morning_server import message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from utils import time_converter
from configs import time_info

db_collection = None


def vi_handler(_, data):
    print('ALARM', data)
    data = data[0]


def start_test():
    market_code = morning_client.get_all_market_code()

    followers = []

    stock_api.subscribe_alarm(morning_client.get_reader(), vi_handler)
    print(len(market_code))
    for code in market_code:
        data = stock_api.request_stock_today_data(morning_client.get_reader(), code)
        print(code, 'receive data', len(data))


if __name__ == '__main__':
    start_test()
