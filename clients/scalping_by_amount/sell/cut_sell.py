from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime, timedelta
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from configs import client_info
from clients.scalping_by_amount.sell import sellmethod
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

import gevent
from utils import trade_logger as logger


class CutSell(sellmethod.SellMethod):
    SATISIFY_PROFIT=1.0125  # 1.25%

    def __init__(self, reader,
                        code_info,
                        market_status,
                        average_price,
                        qty):
        super().__init__(reader, code_info, market_status, average_price, qty, self.handler)
        self.order_num = 0
        self.sell_in_progress = False
        self.sell_start_time = None
        self.minimum_profit_price = average_price * CutSell.SATISIFY_PROFIT

    def tick_handler(self, data):
        pass

    def handler(self, code, tick_data):
        if self.sell_in_progress:
            if self.sell_start_time is not None and datetime.now() - self.sell_start_time > timedelta(seconds=10):
                stock_api.modify_order(self.reader, self.order_num, self.get_code(), self.immediate_sell_price())
        elif (self.get_top_bid() <= self.get_cut_price() or
                    len(self.get_current_available_price_slots()) <= 2 or
                    self.get_minimum_profit_price() <= self.get_top_bid()):
            if self.get_top_bid() <= self.get_cut_price():
                print('REASON meet cut price', 'top bid', self.get_top_bid(), 'cut price', self.get_cut_price())
            elif len(self.get_current_available_price_slots()) <= 2:
                print('REASON current available price slots', self.get_current_available_price_slots())
            elif self.get_minimum_profit_price() <= self.get_top_bid():
                print('REASON meet profit', 'minimum profit', self.get_minimum_profit_price(), 'top bid', self.get_top_bid())

            self.sell_immediately()

    def sell_immediately(self):
        super().sell_immediately()

        logger.info('ENTER SELL IMMEDIATELY FLAG: %s, iprice: %d',
                    str(self.sell_in_progress),
                    self.get_immediate_sell_price())
        if not self.sell_in_progress and self.get_immediate_sell_price() != 0:
            result = stock_api.order_stock(self.reader, self.get_code(), self.get_immediate_sell_price(), self.get_current_quantity(), False)
            self.sell_in_progress = True
        else:
            logger.warning('CANNOT DO SELL IMMEDIATELY')

    def receive_result(self, result):
        if result['flag'] == '4':
            # In case of cancle and modify, check in flag '2'
            self.order_num = result['order_number']
        elif result['flag'] == '1':
            self.decrement_quantity(result['quantity'])

            if self.get_current_quantity() == 0:
                pass
            else:
                self.sell_start_time = datetime.now()
        elif result['flag'] == '2':
            self.sell_start_time = datetime.now()
