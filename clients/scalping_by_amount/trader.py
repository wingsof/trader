from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

from morning.pipeline.converter import dt
from clients.scalping_by_amount.buystage import BuyStage
from clients.scalping_by_amount.sellstage import SellStage
from clients.scalping_by_amount import tradestatus
from utils import trade_logger as logger

import gevent


class Trader:
    def __init__(self, reader, code_info, market_status):
        self.reader = reader
        self.code_info = code_info
        self.market_status = market_status
        self.stage = None

    def start(self):
        logger.warning('START BUY STAGE %s', self.code_info['code'])
        self.stage = BuyStage(self.reader, self.code_info, self.market_status)

    def finish_work(self):
        if self.stage is not None and isinstance(self.stage, SellStage):
            self.stage.sell_immediately()

    def receive_result(self, result):
        if 'flag' not in result or 'quantity' not in result or 'code' not in result:
            logger.error('RESULT without flag or quantity %s', str(result))
            return

        if result['code'] != self.code_info['code']:
            return
        #print('receive result', self.code_info['code'])
        if self.stage is None:
            logger.error('RECEIVE RESULT but stage None %s', str(result))
        else:
            self.stage.receive_result(result)

    def top_edge_detected(self):
        logger.info('TOP EDGE DETECTED %s', self.code_info['code'])
        if isinstance(self.stage, SellStage):
            self.stage.sell_immediately()

    def bottom_edge_detected(self):
        logger.info('BOTTOM EDGE DETECTED')

    def tick_data_handler(self, data):
        if self.stage is not None:
            self.stage.tick_handler(data)

    def ba_data_handler(self, code, tick_data):
        # Use BA callback as timer to process order
        if self.stage is not None:
            self.stage.ba_data_handler(code, tick_data)
            if isinstance(self.stage, BuyStage):
                if self.stage.get_status() == tradestatus.BUY_FAIL:
                    self.stage = None
                elif self.stage.get_status() == tradestatus.BUY_SOME:
                    self.stage.cancel_remain()
                elif self.stage.get_status() == tradestatus.BUY_DONE:
                    average_price, qty = self.stage.get_buy_average()
                    self.stage = SellStage(self.reader, self.code_info, self.market_status, average_price, qty)
            elif isinstance(self.stage, SellStage):
                if self.stage.is_finished():
                    self.stage = None

    def is_finished(self):
        return self.stage is None
