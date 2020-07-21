import gevent
import math
import simulstatus
import markettime
from order import Order
from datetime import timedelta

import stock_provider_pb2 as stock_provider


class OrderSheet:
    def __init__(self, code, order_callback):
        self.order_callback = order_callback
        self.code = code
        self.buy = []
        self.sell = []

    def add_new_order(self, t, order):
        if order.is_buy:
            self.buy.append(Order(self.code, order, self.order_changed_callback))
        else:
            self.sell.append(Order(self.code, order, self.order_changed_callback))

    def change_order(self, t, order):
        pass

    def order_changed_callback(self, is_buy, price, qty):
        print('order changed')

class Spread:
    def __init__(self, code, order_callback):
        self.code = code

        self.price = 0
        self.bid_price = 0
        self.ask_price = 0
        self.bid_remains = []
        self.ask_remains = []
        self.order_callback = order_callback
        self.is_in_market = False
        self.buy_or_sell = True

        self.ask_spread = []
        self.bid_spread = []

        self.order = OrderSheet(code, self.order_callback)

    def get_immediate_price(self, is_buy):
        if is_buy and len(self.ask_spread) > 0:
            if len(self.ask_spread) > 2:
                return self.ask_spread[2]
            else:
                return self.ask_spread[-1]
        elif not is_buy and len(self.bid_spread) > 0:
            if len(self.bid_spread) > 2:
                return self.bid_spread[2]
            else:
                return self.bid_spread[-1]
        print('Cannot find immmediate price', is_buy, self.bid_spread, self.ask_spread)
        return 0

    def get_sell_available(self):
        if self.order is not None:
            return self.order.sell.available_qty 
        return 0

    def set_price_info(self, bs, p, b, a, status):
        self.buy_or_sell = bs
        self.price = p
        self.bid_price = b
        self.ask_price = a
        self.is_in_market = (status == 50)
        #self.order.price_updated(bs, p, b, a, self.is_in_market)

    def set_spread_info(self, bp, ap, br, ar):
        self.ask_spread = ap
        self.bid_spread = bp
        self.bid_remains = br
        self.ask_remains = ar

    def is_new_order(self, m):
        if (m == stock_provider.OrderMethod.TRADE_IMMEDIATELY or
            m == stock_provider.OrderMethod.TRADE_ON_BID_ASK_MEET or
            m == stock_provider.OrderMethod.TRADE_ON_PRICE):
            return True
        return False

    def add_order(self, t, cash, order):
        if order.method == stock_provider.OrderMethod.TRADE_IMMEDIATELY:
            if order.is_buy and order.percentage > 0:
                order.quantity = int(cash * order.percentage / 100.0 / order.price)
            elif not order.is_buy and order.percentage > 0:
                order.quantity = int(math.ceil(self.get_sell_available() * order.percentage / 100))
            # Later consider this case, when no available sell but want 50% sell in specific price
        if self.is_new_order() and order.quantity == 0:
            print('Order quantity is zero')
            return
        
        if not self.is_new_order() and not order.method == stock_provider.OrderMethod.TRADE_UNKNOWN:
            self.order.change_order(t, order)
        else:
            self.order.add_new_order(t, order)
