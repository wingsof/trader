from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from datetime import datetime, timedelta
from clients.scalping_by_amount import tradestatus
from clients.scalping_by_amount import price_info
from clients.scalping_by_amount import orderqueue as oq
from clients.scalping_by_amount.sell import sellmethod
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


class MinimumProfit(sellmethod.SellMethod):
    def __init__(self, reader, code_info, market_status, average_price, qty):
        super().__init__(reader, code_info, market_status, average_price, qty, self.handler)
        self.status = -1
        self.point_price = -1
        self.current_cut_step = -3
        self.order_queue = oq.OrderQueue()
        self.finalize_orders = []
        self.traded_sheet = []
        self.finish_flag = False
        self.set_status(tradestatus.SELL_WAIT)

    def set_status(self, status):
        if status != self.status:
            logger.info('SELL STATUS %s to %s',
                    tradestatus.status_to_str(self.status), 
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
        self.status = status

    def get_status(self):
        return self.status

    def tick_handler(self, data):
        pass

    def sell_immediately(self):
        super().sell_immediately()
        logger.info('ENTER SELL IMMEDIATELY FLAG: %s, STATUS %s, iprice: %d',
                    str(self.finish_flag),
                    tradestatus.status_to_str(self.get_status()),
                    self.immediate_sell_price)
        if not self.finish_flag and self.get_status() == tradestatus.SELL_PROGRESSING and self.get_immediate_sell_price() != 0:
            self.finish_flag = True
            order_list = self.order_queue.get_ready_order_list()
            self.finalize_orders = self.order_queue.get_in_transaction_order_list()
            for order in order_list:
                order.set_cut_order(self.get_immediate_sell_price())
                order_num_org = order.order_number
                result = stock_api.modify_order(self.reader, order.order_number, self.code_info['code'], order.price)
                order.order_number = result['order_number'] # new order number
                logger.warning('MODIFY ORDER RETURN(EXIT, %d): %s', order_num_org, str(result))
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
        self.point_price = self.get_top_bid()
        price_slots = self.get_price_slots(self.get_slots(), self.get_minimum_profit_price(), self.get_current_quantity())
        if len(price_slots) == 0:
            if self.get_immediate_sell_price() != 0:
                self.process_sell_order(code, [(self.get_immediate_sell_price(), self.get_current_quantity())])
            else:
                logger.error('CANNOT FIND IMMEDIATE SELL PRICE')
        else:
            order_sheet = price_info.create_order_sheet(price_slots, self.qty)
            self.process_sell_order(code, order_sheet)

    def handle_cut_off(self, code):
        ba_unit = self.get_current_bidask_unit()
        price_step = (self.get_top_bid() - self.point_price) / ba_unit
        print('price_step', price_step, 'currnet point', self.point_price, 'current bid', self.get_top_bid(), 'order remain', len(self.order_queue),
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
                order_number_org = order.order_number
                order.order_number = result['order_number'] # new order number
                logger.warning('MODIFY ORDER RETURN(CUT, %d): %s', order_number_org, str(result))

    def handler(self, code, tick_data):
        if self.finish_flag:
            if len(self.finalize_orders) > 0:
                self.finish_flag = False
                self.sell_immediately()
            return
        elif self.get_status() == tradestatus.SELL_WAIT:
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
            order.modify(tradestatus.SELL_ORDER_IN_TRANSACTION, top_price)
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
            self.set_quantity(0) 
            self.set_status(tradestatus.SELL_DONE)
