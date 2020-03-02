from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime

import gevent


class Trader:
    STATUS_NONE = 0
    def __init__(self):
        self.target_price = 0
        self.balance = stock_api.get_balance

    def ba_data_handler(self. code, data):
        if self.target_price = 0:
