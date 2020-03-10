from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime, timedelta
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from clients.scalping_by_amount import orderqueue as oq
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount import mock_stock_api as stock_api
else:
    from morning_server import stock_api

import gevent
from utils import trade_logger as logger


MAX_SLOT=3


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
        self.previous_current_bid = -1
        self.point_price = -1
        self.current_cut_step = -2
        self.immediate_sell_price = 0
        self.order_queue = oq.OrderQueue()
        self.traded_sheet = []
        self.finish_flag = False
        logger.info('SellStage START, average_price: %d, qty: %d', average_price, qty)
        self.set_status(tradestatus.SELL_WAIT)

    def set_status(self, status):
        before = self.status
        self.status = status
        if before != self.status:
            logger.info('SELL STATUS %s to %s',
                    tradestatus.status_to_str(before), 
                    tradestatus.status_to_str(status))
            if status == tradestatus.SELL_DONE:
                total_buy = self.average_price * self.qty
                total_sell = sum([ts['price'] * ts['quantity'] for ts in self.traded_sheet])
                total_sell = total_sell * 0.9975
                profit = (total_sell - total_buy) / total_buy * 100
                logger.warning('TRADED RESULT(%s) PROFIT: %s, AMOUNT: %d',
                                self.code_info['code'],
                                str(float("{0:.2f}".format(profit))),
                                (total_sell - total_buy))

    def get_status(self):
        return self.status

    def tick_handler(self, data):
        pass

    def sell_immediately(self):
        logger.info('ENTER SELL IMMEDIATELY FLAG: %s, STATUS %s, iprice: %d',
                    str(self.finish_flag),
                    tradestatus.status_to_str(self.get_status()),
                    self.immediate_sell_price)
        if not self.finish_flag and self.get_status() == tradestatus.SELL_PROGRESSING and self.immediate_sell_price != 0:
            self.finish_flag = True
            order_list = self.order_queue.get_ready_order_list()
            for order in order_list:
                order.set_cut_order(self.immediate_sell_price)
                result = stock_api.modify_order(self.reader, order.order_number, self.code_info['code'], order.price)
                order.order_number = result['order_number'] # new order number
                logger.warning('MODIFY ORDER RETURN(EXIT): %s', str(result))
        else:
            logger.warning('CANNOT DO SELL IMMEDIATELY')

    def process_sell_order(self, code, order_sheet):
        # for preventing ba_data_handler reentered and call process_sell_order
        for order in order_sheet:
            price = order[0]
            qty = order[1]
            logger.info('PROCESS SELL ORDER(%s) price: %d, qty: %d',
                        code, price, qty) 
            result = stock_api.order_stock(self.reader, code, price, qty, False)
            if result['status'] == 0:
                self.order_queue.add_order(price, qty)
            logger.warning('SELL ORDER RETURN: %s', str(result))


    def start_sell_order(self, code):
        self.set_status(tradestatus.SELL_PROGRESSING)
        self.point_price = self.current_bid
        price_slots = self.get_price_slots(self.slots, self.minimum_profit_price, self.qty)
        if len(price_slots) == 0 or self.edge_found:
            if self.immediate_sell_price != 0:
                self.process_sell_order(code, [(self.immediate_sell_price, self.qty)])
            else:
                logger.error('CANNOT FIND IMMEDIATE SELL PRICE')
        else:
            order_sheet = price_info.create_order_sheet(price_slots, self.qty)
            self.process_sell_order(code, order_sheet)

    def handle_cut_off(self, code):
        ba_unit = price_info.get_ask_bid_price_unit(self.point_price, self.code_info['is_kospi'])
        price_step = (self.current_bid - self.point_price) / ba_unit
        print('price_step', price_step, 'currnet point', self.point_price, 'current bid', self.current_bid, 'order remain', len(self.order_queue),
                'asks', self.order_queue.get_price_list())
        if price_step <= self.current_cut_step and len(self.order_queue) > 0:
            order = self.order_queue.get_ready_top_order()
            if order is None:
                logger.warning('TOP ORDER ITEM is in transaction')
            else:
                self.current_cut_step = -1
                self.point_price = self.current_bid
                logger.info('CHANGE point price as %d', self.point_price)
                order.set_cut_order(self.current_bid) # put order status to SELL_ORDER_IN_TRANSACTION
                result = stock_api.modify_order(self.reader, order.order_number, code, order.price)
                order.order_number = result['order_number'] # new order number
                logger.warning('MODIFY ORDER RETURN(CUT): %s', str(result))

    def ba_data_handler(self, code, tick_data):
        self.current_bid = tick_data['first_bid_price']
        if self.previous_current_bid != self.current_bid:
            logger.info('FIRST BID CHANGED TO %d', self.current_bid)

        self.immediate_sell_price = price_info.get_immediate_sell_price(tick_data, self.order_queue.get_all_quantity())
        self.slots = price_info.create_slots(
                self.code_info['yesterday_close'],
                self.current_bid,
                self.code_info['today_open'],
                self.code_info['is_kospi'])
        if self.get_status() == tradestatus.SELL_WAIT:
            self.start_sell_order(code)
        elif self.get_status() == tradestatus.SELL_PROGRESSING:
            self.handle_cut_off(code)

        timeout_list = self.order_queue.get_ready_timeout_order()
        for order in timeout_list:
            order.set_cut_order(self.immediate_sell_price) 
            result = stock_api.modify_order(self.reader, order.order_number, code, order.price)
            order.order_number = result['order_number'] # new order number
            logger.warning('MODIFY ORDER RETURN(TIMEOUT): %s', str(result))
        self.previous_current_bid = self.current_bid

    def move_to_top(self, order):
        price_slots = self.get_current_available_price_slots()
        top_price = 0
        if len(self.order_queue) == 1:
            top_price = order.price
        else:
            top_price = self.order_queue.get_max_price()
        
        for p in price_slots:
            if top_price < p:
                top_price = p
                break
        
        if top_price != order.price:
            order.status = tradestatus.SELL_ORDER_IN_TRANSACTION
            order.price = top_price
            result = stock_api.modify_order(self.reader, order.order_number, self.code_info['code'], order.price)
            order.order_number = result['order_number'] # new order number
            logger.warning('MODIFY ORDER RETURN(MOVE TO TOP): %s', str(result))

    def receive_result(self, result):
        if result['flag'] == '4':
            # In case of cancle and modify, check in flag '2'
            order_list = self.order_queue.find_new_order(result['price'], result['quantity'])
            if len(order_list) != 1:
                logger.warning('FOUND MORE THAN 1 order or MODIFY length %d', len(order_list))
            else:
                order = order_list[0]
                order.order_number = result['order_number']
                order.status = tradestatus.SELL_ORDER_READY
        elif result['flag'] == '1':
            order = self.order_queue.get_order_by_order_num(result['order_number'])
            if order is None:
                logger.warning('CANNOT FIND ORDER BY ORDER NUM %d', result['order_number'])
            else:
                order.order_quantity -= result['quantity']
                self.point_price = order.price
                self.traded_sheet.append({'price': order.price, 'quantity': result['quantity']})
                if order.order_quantity == 0:
                    self.order_queue.remove_order(order)
                else:
                    if not order.is_cut and order.order_quantity <= order.order_quantity_org / 2:
                        self.move_to_top(order)
        elif result['flag'] == '2':
            # modify, cancel
            order = self.order_queue.get_order_by_order_num(result['order_number'])
            if order is None:
                logger.warning('CANNOT FIND ORDER BY ORDER NUM %d', result['order_number'])
            else:
                if order.is_cancel_progressing: # still no case to cancel order
                    order.order_quantity = 0
                    self.order_queue.remove_order(order)
                else: # modify
                    order.order_quantity = result['quantity']
                    order.order_price = result['price']
                    order.status = tradestatus.SELL_ORDER_READY

        if len(self.order_queue) == 0:
            self.set_status(tradestatus.SELL_DONE)

    def get_current_available_price_slots(self):
        price_slot = price_info.upper_available_empty_slots(self.slots)
        return list(filter(lambda x: x > self.minimum_profit_price, price_slot))

    def get_price_slots(self, slots, mprice, qty):
        price_slot = price_info.upper_available_empty_slots(slots)
        profit_slot = list(filter(lambda x: x > mprice, price_slot))
        if len(price_slot) == 0:
            logger.error('NO PROFIT SLOT')
            return []

        logger.info('AVAILABLE PROFIT SLOT len(%d), START FROM %d',
                    len(profit_slot), profit_slot[0])
        if len(profit_slot) > MAX_SLOT:
            profit_slot = profit_slot[:MAX_SLOT]
        
        while qty / len(profit_slot) < 0:
            profit_slot = profit_slot[:-1]

        return profit_slot
