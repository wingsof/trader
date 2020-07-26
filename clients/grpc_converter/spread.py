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
        self.company_name = ''
        self.total_quantity = 0
        self.hold_average = [0, 0] # price, quantity
        self.current_profit = 0.0
        self.cut_rate = 0.0
        self.buy = []
        self.sell = []

    def get_total_quantity(self):
        return self.total_quantity

    def add_new_order(self, order):
        new_order = Order(self.code, self.company_name, order, 0, self.order_changed_callback)

        result = new_order.request()
        if result[0] != 0:
            print('ORDER FAILED', result[1])
            return

        if order.is_buy:
            self.buy.append(new_order)
        else:
            self.sell.append(new_order)

    def change_order(self, order):
        all_orders = []
        all_orders.extend(self.buy)
        all_orders.extend(self.sell)
        for ao in all_orders:
            print(order.order_num, ao.order_num, ao.internal_order_num, ao.quantity)
            if (order.order_num == ao.order_num or order.order_num == ao.internal_order_num) and ao.quantity > 0:
                return ao.change_order(order)

        return False

    def get_remain_sell_count(self):
        count = 0
        for s in self.sell:
            if s.quantity > 0:
                count += 1
        return count

    def order_changed_callback(self, status, is_buy, price, qty, total_qty):
        if status == stock_provider.OrderStatusFlag.STATUS_TRADED:
            # TODO: Handle partial buy traded
            self.total_quantity = total_qty
            if is_buy:
                self.hold_average[0] = (self.hold_average[0] * self.hold_average[1] + price * qty) / (self.hold_average[1] + qty)
                self.hold_average[1] = self.hold_average[1] + qty
            else:
                self.hold_average[1] -= qty
                self.current_profit += (price - self.hold_average[0]) * qty

            print(is_buy, self.total_quantity, self.get_remain_sell_count())
            if is_buy and self.total_quantity > 0 and self.get_remain_sell_count() == 0:
                if self.cut_rate == 0.0:
                    self.create_sell_order()
                    
        self.send_report()

    def price_updated(self, bs, p, b, a, status):
        pass # find registered status and MEET_ON_BA

    def create_sell_order(self):
        sell_order = stock_provider.OrderMsg(code=self.code,
                                             is_buy=False,
                                             price=0,
                                             quantity=self.total_quantity,
                                             percentage=0,
                                             method=stock_provider.OrderMethod.TRADE_UNKNOWN,
                                             order_num='',
                                             order_type=stock_provider.OrderType.NEW)
        self.sell.append(Order(self.code, self.company_name, sell_order, self.hold_average[0], self.order_changed_callback))

    def send_report(self):
        orders = []
        for b in self.buy:
            orders.append(b.convert_to_report())

        for s in self.sell:
            orders.append(s.convert_to_report())

        self.order_callback(orders)
        self.print_orders()

    def print_orders(self):
        print('-' * 50)
        print('TOTAL QUANTITY: ' + str(self.total_quantity))
        for b in self.buy:
            if b.quantity > 0:
                print(str(b))

        for s in self.sell:
            if s.quantity > 0:
                print(str(s))


class Spread:
    def __init__(self, code, order_callback):
        self.code = code
        self.company_name = ''
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

        self.ordersheet = OrderSheet(code, self.order_callback)

    def has_company_name(self):
        return len(self.company_name) > 0

    def set_company_name(self, cname):
        self.company_name = cname
        self.ordersheet.company_name = cname

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
        if self.ordersheet is not None:
            return self.ordersheet.get_total_quantity()
        return 0

    def set_price_info(self, bs, p, b, a, status):
        self.buy_or_sell = bs
        self.price = p
        self.bid_price = b
        self.ask_price = a
        self.is_in_market = (status == 50)
        self.ordersheet.price_updated(bs, p, b, a, status)

    def set_spread_info(self, bp, ap, br, ar):
        self.ask_spread = ap
        self.bid_spread = bp
        self.bid_remains = br
        self.ask_remains = ar

    def add_order(self, cash, order):
        if order.order_type == stock_provider.OrderType.NEW:
            if order.method == stock_provider.OrderMethod.TRADE_IMMEDIATELY:
                order.price = self.get_immediate_price(order.is_buy)
                if order.price == 0:
                    print('Price is zero')
                    return

                if order.is_buy and order.percentage > 0:
                    order.quantity = int(cash * order.percentage / 100.0 / order.price)
                elif not order.is_buy and order.percentage > 0:
                    order.quantity = int(math.ceil(self.get_sell_available() * order.percentage / 100))
                # Later consider this case, when no available sell but want 50% sell in specific price

            if order.quantity == 0 or order.price == 0:
                print('Order quantity or price is zero', order.quantity, order.price)
                return
            self.ordersheet.add_new_order(order)
        elif order.order_type == stock_provider.OrderType.MODIFY: 
            self.ordersheet.change_order(order)
