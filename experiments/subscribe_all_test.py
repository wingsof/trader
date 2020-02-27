from gevent import monkey; monkey.patch_all()
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 1))))


from clients.common import morning_client
from datetime import datetime, date, timedelta, time
from morning.back_data import holidays
from morning_server import stock_api, message
import gevent
from gevent.queue import Queue
from configs import db
from pymongo import MongoClient
from morning.pipeline.converter import dt
import numpy as np
from scipy.signal import find_peaks, peak_prominences
import pandas as pd


def wait_loop():
    while True:
        gevent.sleep(0.03)


def tick_data_handler(code, data):
    if len(data) != 1:
        return
    print(data[0])


market_code = morning_client.get_market_code() # KOSDAQ
kospi_market_code = morning_client.get_market_code(message.KOSPI)

market_code.extend(kospi_market_code)
print('all', len(market_code))

for code in market_code:
    stock_api.subscribe_stock(morning_client.get_reader(), code, tick_data_handler)


gevent.joinall([gevent.spawn(wait_loop)])
