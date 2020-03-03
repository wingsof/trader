from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime
from clients.scalping_by_amount import price_info
from clients.scalping_by_amount.buystage import BuyStage

import gevent


class Trader:
    def __init__(self, reader, code_info, market_status):
        self.reader = reader
        self.code_info = code_info
        self.balance = stock_api.get_balance(self.reader)
        self.stage = None
        """
        {'code': self.code, 'amount': amount, 'profit': profit,
        'yesterday_close': yesterday_close, 'today_open': self.open_price,
        'current_price': current_close, 'is_kospi': self.is_kospi}
        """
    def start(self):
        self.stage = BuyStage(reader, market_status, self.interrupted, int(self.balance / 10))

    def interrupted(self):
        if self.stage is None:
            print('Something wrong')
        elif isinstance(self.stage, BuyStage):
            self.stage = None

    def receive_result(self, resut):
        if self.stage is None:
            print('Something wrong', result)
        elif isinstance(self.stage, BuyStage):
            is_done = self.stage.process_result(result)
            if is_done:
                average_price, qty = self.stage.get_buy_average()
        else: # SellStage
            pass

    def tick_handler(self, data):
        if self.stage is not None:
            self.stage.tick_handler(data)

    def ba_data_handler(self, code, tick_data):
        if self.stage is not None:
            self.stage.ba_data_handler(code, tick_data)
