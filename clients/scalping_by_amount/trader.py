from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount import tradestatus

import gevent


class Trader:
    def __init__(self, reader, code_info, market_status):
        self.reader = reader
        self.code_info = code_info
        self.balance = stock_api.get_balance(self.reader)
        print('*' * 50, 'CURRENT BALANCE', self.balance, '*' * 50)
        self.market_status = market_status
        self.stage = None

    def start(self):
        self.stage = BuyStage(self.reader, self.market_status, int(self.balance / 10))

    def receive_result(self, resut):
        if 'flag' not in result or 'quantity' not in result:
            print('result something wrong', result)
            return

        print('*' * 50, '\nTRADE RESULT\n', result, '\n', '*' * 50)
        if self.stage is None:
            print('STAGE IS NONE')
        else:
            self.stage.receive_result(result)

    def tick_handler(self, data):
        if self.stage is not None:
            self.stage.tick_handler(data)

    def ba_data_handler(self, code, tick_data):
        # Use BA callback as timer to process order
        if self.stage is not None:
            self.stage.ba_data_handler(code, tick_data)
            if isinstance(self.stage, BuyStage):
                if self.stage.get_status() == tradestatus.BUY_FAIL:
                    pass
                elif self.stage.get_status() == tradestatus.BUY_SOME:
                    # Try cancel order remained
                    pass
                elif self.stage.get_status() == tradestatus.BUY_DONE:
                    average_price, qty = self.stage.get_buy_average()
                    self.stage = SellStage(self.reader, self.code_info, self.market_status, average_price, qty)
            elif isinstance(self.stage, SellStage):
                if self.stage.get_status() == tradestatus.SELL_DONE:
                    self.stage = None

    def is_finished(self):
        return self.stage is None
