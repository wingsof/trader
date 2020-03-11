from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import timedelta
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


DEFAULT_TIMEOUT=timedelta(seconds=60*5)


class _OrderItem:
    def __init__(self, price, qty):
        self.price = price
        self.order_quantity = qty
        self.order_quantity_org = qty
        self.order_number = 0
        self.order_time = datetime.now()
        self.is_cancel_progressing = False
        self.is_cut = False
        self.status = tradestatus.SELL_ORDER_IN_TRANSACTION

    def modify(self, status, price):
        self.status = status
        self.price = price
        self.order_time = datetime.now()

    def set_cut_order(self, price):
        self.modify(tradestatus.SELL_ORDER_IN_TRANSACTION, price)
        self.is_cut = True # for identifying put at high price or keep price

class OrderQueue:
    def __init__(self):
        self.queue = []

    def get_ready_order_list(self):
        order_list = []
        for order in self.queue:
            if order.status == tradestatus.SELL_ORDER_READY:
                order_list.append(order)
        return order_list

    def add_order(self, price, qty):
        self.queue.append(_OrderItem(price, qty))

    def get_all_quantity(self):
        return sum([o.order_quantity for o in self.queue])

    def __len__(self):
        return len(self.queue)

    def get_price_list(self):
        return [o.price for o in self.queue]

    def get_ready_top_order(self):
        order_list = self.get_ready_order_list()
        sort_by_price = sorted(order_list, key=lambda x: x.price, reverse=True)
        if len(sort_by_price) > 0:
            return sort_by_price[0]
        return None

    def get_max_price(self):
        return max([d.price for d in self.queue])

    def get_order_by_order_num(self, order_num):
        for order in self.queue:
            if order.order_number == order_num:
                return order
        return None

    def find_new_order(self, price, qty):
        order_list = []
        for order in self.queue:
            if order.price == price and order.order_quantity == qty and order.order_number == 0:
                order_list.append(order)
        return order_list

    def remove_order(self, order):
        self.queue.remove(order)

    def get_ready_timeout_order(self):
        timeout_list = []
        order_list = self.get_ready_order_list()
        for order in order_list:
            if datetime.now() - order.order_time > DEFAULT_TIMEOUT:
                timeout_list.append(order)
        return timeout_list
