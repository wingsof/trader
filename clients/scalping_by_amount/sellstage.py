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


MAX_SLOT=5


class OrderItem:
    def __init__(self, price, qty):
        self.price = price
        self.order_quantity = qty
        self.order_number = 0
        self.order_time = datetime.now()
        self.is_cancel_progressing = False
        self.is_cut = False
        self.status = tradestatus.SELL_ORDER_IN_TRANSACTION

    def set_cut_order(self, price):
        self.price = price
        self.status = tradestatus.SELL_ORDER_IN_TRANSACTION
        self.is_cut = True # for identifying put at high price or keep price


class SellStage:
    def __init__(self, reader, code_info, market_status, average_price, qty, edge_found):
        self.reader = reader
        self.code_info = code_info
        self.market_status = market_status
        self.average_price = average_price
        self.minimum_profit_price = self.average_price * 1.0025
        self.qty = qty
        self.slots = None
        self.edge_found = edge_found
        self.status = -1
        self.current_bid = -1
        self.point_price = -1
        self.current_cut_step = -2
        self.immediate_sell_price = 0
        self.order_in_queue = []
        self.finish_flag = False
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

    def sell_immediately(self):
        #TODO:  CALCULATE PRICE for immediately (not just first bid)
        if not self.finish_flag and self.get_status() == tradestatus.SELL_PROGRESSING and self.immediate_sell_price != 0:
            self.finish_flag = True
            for order in self.order_in_queue:
                if order.status == tradestatus.SELL_ORDER_READY:
                    order.set_cut_order(self.immediate_sell_price)
                    result = stock_api.modify_order(self.reader, order.order_number, self.code_info['code'], order.price)
                    order.order_number = result['order_number'] # new order number
                    print('*' * 20, '\nMODIFY ORDER RETURN(EXIT)\n', result, '*' * 20)
        else:
            print('*' * 50, 'ERROR cannot process sell immediately', '*' * 50)
            print('finish_flag', self.finish_flag, 'status', self.get_status(), 'immediate price', self.immediate_sell_price)

    def process_sell_order(self, code, order_sheet):
        # for preventing ba_data_handler reentered and call process_sell_order
        for order in order_sheet:
            price = order[0]
            qty = order[1]
            print('*' * 20, 'process sell order', code, 'price:', price, 'qty:', qty, '*' * 20)
            result = stock_api.order_stock(self.reader, code, price, qty, False)
            if result['status'] == 0:
                self.order_in_queue.append(OrderItem(price, qty))
            print('-' * 30, '\nSELL ORDER RETURN\n', result, '\n', '-' * 30)

    def ba_data_handler(self, code, tick_data):
        self.current_bid = tick_data['first_bid_price']
        self.immediate_sell_price = price_info.get_immediate_sell_price(tick_data, self.order_in_queue)
        self.slots = price_info.create_slots(
                self.code_info['yesterday_close'],
                self.current_bid,
                self.code_info['today_open'],
                self.code_info['is_kospi'])
        if self.get_status() == tradestatus.SELL_WAIT:
            self.set_status(tradestatus.SELL_PROGRESSING)
            self.point_price = self.current_bid
            price_slots = self.get_price_slots(self.slots, self.minimum_profit_price, self.qty)
            if len(price_slots) == 0 or self.edge_found:
                if self.immediate_sell_price != 0:
                    self.process_sell_order(code, [(self.immediate_sell_price, self.qty)])
                else:
                    print('*' * 50, 'ERROR cannot find immediate sell price', '*' * 50)
            else:
                order_sheet = price_info.create_order_sheet(price_slots, self.qty)
                self.process_sell_order(code, order_sheet)
        elif self.get_status() == tradestatus.SELL_PROGRESSING:
            ba_unit = price_info.get_ask_bid_price_unit(self.point_price, self.code_info['is_kospi'])
            price_step = (self.current_bid - self.point_price) / ba_unit
            print('price_step', price_step, 'currnet point', self.point_price, 'current bid', self.current_bid, 'order remain', len(self.order_in_queue),
                    'asks', [o.price for o in self.order_in_queue])
            if price_step <= self.current_cut_step and len(self.order_in_queue) > 0:
                order = self.order_in_queue[-1]
                if order.status == tradestatus.SELL_ORDER_READY:
                    self.current_cut_step = -1
                    self.point_price = self.current_bid
                    self.order_in_queue.remove(order)
                    self.order_in_queue.insert(0, order)
                    order.set_cut_order(self.current_bid) # put order status to SELL_ORDER_IN_TRANSACTION
                    result = stock_api.modify_order(self.reader, order.order_number, code, order.price)
                    order.order_number = result['order_number'] # new order number
                    print('-' * 30, '\nMODIFY ORDER RETURN\n', result, '\n', '-' * 30)
                else:
                    print('TOP ORDER ITEM is in transaction')

    def move_to_top(self, order):
        price_slots = self.get_current_available_price_slots()
        top_price = 0
        if len(self.order_in_queue) == 1:
            top_price = order.price
        else:
            top_price = max([d.price for d in self.order_in_queue])
        
        for p in price_slots:
            if top_price < p:
                top_price = p
                break
        
        if top_price != order.price:
            order.status = tradestatus.SELL_ORDER_IN_TRANSACTION
            order.price = top_price
            self.order_in_queue.remove(order)
            self.order_in_queue.append(order)
            result = stock_api.modify_order(self.reader, order.order_number, self.code_info['code'], order.price)
            order.order_number = result['order_number'] # new order number
            print('*' * 20, '\nMODIFY ORDER RETURN\n', result, '*' * 20)

    def receive_result(self, result):
        if result['flag'] == '4':
            for order in self.order_in_queue:
                if order.price == result['price'] and order.order_quantity == result['quantity']:
                    if order.order_number == 0: # buy, sell
                        order.order_number = result['order_number']
                        order.status = tradestatus.SELL_ORDER_READY
                        break
                    elif order.order_number == result['order_number']: # cancel, modify
                        break
                    else:
                        print('CANNOT FIND ITEM')
        elif result['flag'] == '1':
            order_done = None
            for order in self.order_in_queue:
                if order.order_number == result['order_number']:
                    order.order_quantity -= result['quantity']
                    self.point_price = order.price
                    if order.order_quantity == 0:
                        order_done = order
                    else:
                        pass
                        #if not order.is_cut:
                        #    self.move_to_top(order)
                    break
            if order_done is not None:
                self.order_in_queue.remove(order)
        elif result['flag'] == '2':
            # modify, cancel
            order_done = None
            for order in self.order_in_queue:
                if order.order_number == result['order_number']:
                    if order.is_cancel_progressing: # still no case to cancel order
                        order.order_quantity = 0
                        order_done = order
                    else: # modify
                        order.order_quantity = result['quantity']
                        order.order_price = result['price']
                        order.status = tradestatus.SELL_ORDER_READY
                    break
            if order_done is not None:
                self.order_in_queue.remove(order)

        if len(self.order_in_queue) == 0:
            self.set_status(tradestatus.SELL_DONE)

    def get_current_available_price_slots(self):
        price_slot = price_info.upper_available_empty_slots(self.slots)
        return list(filter(lambda x: x > self.minimum_profit_price, price_slot))

    def get_price_slots(self, slots, mprice, qty):
        price_slot = price_info.upper_available_empty_slots(slots)
        profit_slot = list(filter(lambda x: x > mprice, price_slot))
        if len(price_slot) == 0:
            print('ERROR) no profit slot')
            return []

        print('available profit slot', len(profit_slot), 'start from', profit_slot[0])
        if len(profit_slot) > MAX_SLOT:
            profit_slot = profit_slot[:MAX_SLOT]
        
        while qty / len(profit_slot) < 0:
            profit_slot = profit_slot[:-1]

        return profit_slot
