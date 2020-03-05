from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount import mock_stock_api as stock_api
else:
    from morning_server import stock_api

import gevent


MAX_SLOT=10


class OrderItem:
    def __init__(self, price, qty):
        self.price = price
        self.order_quantity = qty
        self.order_number = 0
        self.order_time = datetime.now()
        self.is_cancel_progressing = False


class SellStage:
    def __init__(self, reader, code_info, market_status, average_price, qty):
        self.reader = reader
        self.code_info = code_info
        self.market_status = market_status
        self.average_price = average_price
        self.minimum_profit_price = self.average_price * 1.0025
        self.qty = qty
        self.slots = None
        self.status = -1
        self.current_bid = -1
        self.point_price = -1
        self.current_cut_step = -2
        self.order_in_queue = []
        self.set_status(tradestatus.SELL_WAIT)

    def set_status(self, status):
        before = self.status
        self.status = status
        if before != self.status:
            print('*' * 10, 'SELL STATUS', tradestatus.status_to_str(before), 'TO', tradestatus.status_to_str(status), '*' * 10)

    def get_status(self):
        return self.status

    def tick_handler(self, data):
        pass

    def process_sell_order(self, code, order_sheet):
        # for preventing ba_data_handler reentered and call process_sell_order
        self.set_status(tradestatus.SELL_ORDER_SENDING) 
        for order in order_sheet:
            price = order[0]
            qty = order[1]
            print('*' * 20, 'process sell order', code, 'price:', price, 'qty:', qty, '*' * 20)
            result = stock_api.order_stock(self.reader, code, price, qty, False)
            print('*' * 20, '\nSELL ORDER RETURN\n', result, '*' * 20)
            if result['status'] == 0:
                self.order_in_queue.append(OrderItem(price, qty))
        self.set_status(tradestatus.SELL_ORDER_SEND_DONE)

    def ba_data_handler(self, code, tick_data):
        if self.current_bid == tick_data['first_bid_price']:
            return

        self.current_bid = tick_data['first_bid_price']
        self.slots = price_info.create_slots(
                self.code_info['yesterday_close'],
                self.current_bid,
                self.code_info['today_open'],
                self.code_info['is_kospi'])
        if self.get_status() == tradestatus.SELL_WAIT:
            self.point_price = self.current_bid
            price_slots = self.get_price_slots(self.slots, self.minimum_profit_price, self.qty)
            if len(price_slots) == 0:
                self.process_sell_order(code, [(self.current_bid, self.qty)])
            else:
                order_sheet = []
                order_qty = self.qty
                for p in price_slots:
                    if order_qty == 0:
                        break
                    q = int(self.qty / len(price_slots))
                    order_qty -= q
                    order_sheet.append((p, q))
                self.process_sell_order(code, order_sheet)
        elif self.get_status() == tradestatus.SELL_ORDER_SEND_DONE:
            ba_unit = price_info.get_ask_bid_price_unit(self.point_price, self.code_info['is_kospi'])
            price_step = (self.current_bid - self.point_price) / ba_unit

            if price_step <= self.current_cut_step and len(self.order_in_queue) > 0:
                self.current_cut_step = -1

                order = self.order_in_queue[-1]
                self.order_in_queue.remove(order)
                self.order_in_queue.insert(0, order)
                order.price = self.current_bid
                result = stock_api.modify_order(self.reader, order.order_number, code, order.price)
                print('*' * 20, '\nMODIFY ORDER RETURN\n', result, '*' * 20)

    def receive_result(self, result):
        if self.get_status() == tradestatus.SELL_ORDER_SEND_DONE or self.get_status() == tradestatus.SELL_ORDER_SENDING:
            if result['flag'] == 4:
                for order in self.order_in_queue:
                    if order.price == result['price'] and order.order_quantity == result['quantity']:
                        if order.order_number != 0: # cancel, modify
                            order.order_number = result['order_number']
                        else: # buy, sell..
                            order.order_number = result['order_number']
            elif result['flag'] == 1:
                for order in self.order_in_queue:
                    if order.order_number == result['order_number']:
                        order.order_quantity -= result['quantity']
                        break
            elif result['flag'] == 2:
                # modify, cancel
               for order in self.order_in_queue:
                    if order.order_number == result['order_number']:
                        if order.is_cancel_progressing:
                            order.order_quantity = 0
                        else: # modify
                            order.order_quantity = result['order_quantity']
                            order.order_price = result['price']


        if sum([d.order_quantity for d in self.order_in_queue]) == 0:
            self.set_status(tradestatus.SELL_DONE)

    def get_price_slots(self, slots, mprice, qty):
        price_slot = price_info.upper_available_empty_slots(slots)
        profit_slot = list(filter(lambda x: x > mprice, price_slot))
        if len(price_slot) == 0:
            print('ERROR) no profit slot')
            return []

        print('available profit slot', len(profit_slot), 'start from', profit_slot[0])
        if len(profit_slot) > MAX_SLOT:
            profit_slot = profit_slot[:10]
        
        while qty / len(profit_slot) < 0:
            profit_slot = profit_slot[:-1]

        return profit_slot
