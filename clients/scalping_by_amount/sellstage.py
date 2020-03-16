from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime, timedelta
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

import gevent
from utils import trade_logger as logger


MAX_SLOT=3


class SellStage:
    def __init__(self, reader, code_info, market_status, average_price, qty):
        self.reader = reader
        self.code_info = code_info
        self.market_status = market_status
        self.average_price = average_price
        self.minimum_profit_price = self.average_price * 1.0025
        self.cut_price = self.average_price * 0.99
        self.qty = qty
        self.order_num = 0
        self.current_bid = -1
        self.previous_current_bid = -1
        self.point_price = -1
        self.current_cut_step = -2
        self.immediate_sell_price = 0
        self.sell_in_progress = False
        self.sell_start_time = None
        self.traded_sheet = []
        self.finish_flag = False
        logger.info('SellStage START, average_price: %d, qty: %d', average_price, qty)

    def tick_handler(self, data):
        pass

    def is_finished(self):
        return self.qty == 0

    def sell_immediately(self):
        logger.info('ENTER SELL IMMEDIATELY FLAG: %s, iprice: %d',
                    str(self.sell_in_progress),
                    self.immediate_sell_price)
        if not self.sell_in_progress and self.immediate_sell_price != 0:
            result = stock_api.order_stock(self.reader, self.code_info['code'], self.immediate_sell_price, self.qty, False)
            self.sell_in_progress = True
        else:
            logger.warning('CANNOT DO SELL IMMEDIATELY')

    def ba_data_handler(self, code, tick_data):
        self.current_bid = tick_data['first_bid_price']
        if self.previous_current_bid != self.current_bid:
            logger.info('FIRST BID CHANGED TO %d', self.current_bid)

        ba_unit = price_info.get_ask_bid_price_unit(self.current_bid, self.code_info['is_kospi'])
        self.immediate_sell_price = price_info.get_immediate_sell_price(tick_data, self.qty, ba_unit)
        slots = price_info.create_slots(
                    self.code_info['yesterday_close'],
                    self.current_bid,
                    self.code_info['today_open'],
                    self.code_info['is_kospi'])

        if self.sell_in_progress:
            if self.sell_start_time is not None and datetime.now() - self.sell_start_time > timedelta(seconds=10):
                stock_api.modify_order(self.reader, self.order_num, self.code_info['code'], self.immediate_sell_price)
        elif (self.current_bid < self.cut_price or
                    len(self.get_current_available_price_slots(slots)) <= 2):
                self.sell_immediately()
        self.previous_current_bid = self.current_bid

    def receive_result(self, result):
        if result['flag'] == '4':
            # In case of cancle and modify, check in flag '2'
            self.order_num = result['order_number']
        elif result['flag'] == '1':
            self.qty -= result['quantity']

            if self.qty == 0:
                pass
            else:
                self.sell_start_time = datetime.now()
        elif result['flag'] == '2':
            self.sell_start_time = datetime.now()

    def get_current_available_price_slots(self, slots):
        price_slot = price_info.upper_available_empty_slots(slots)
        return list(filter(lambda x: x > self.minimum_profit_price, price_slot))
