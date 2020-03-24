from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime, timedelta
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from clients.scalping_by_amount.sell import immediate_sell
from clients.scalping_by_amount.sell import minimum_profit
from clients.scalping_by_amount.sell import cut_sell
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

import gevent
from utils import trade_logger as logger



class SellStage:
    def __init__(self, reader, code_info, market_status, average_price, qty):
        logger.info('SellStage START, average_price: %d, qty: %d', average_price, qty)
        #self.sell_method = ImmediateSell(reader, code_info, market_status, average_price, qty, minimum_profit_price, cut_price)
        self.sell_method = cut_sell.CutSell(reader, code_info, market_status, average_price, qty)

    def tick_handler(self, data):
        self.sell_method.tick_handler(data)

    def is_finished(self):
        return self.sell_method.is_finished()

    def sell_immediately(self):
        self.sell_method.sell_immediately()

    def ba_data_handler(self, code, tick_data):
        self.sell_method.ba_data_handler(code, tick_data)

    def receive_result(self, result):
        self.sell_method.receive_result(result)
