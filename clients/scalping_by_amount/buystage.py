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

from utils import trade_logger as logger
import gevent


class BuyStage:
    def __init__(self, reader, code_info, market_status, balance):
        self.reader = reader
        self.balance = balance
        self.code_info = code_info
        self.market_status = market_status
        self.quantity = 0
        self.order_done = False
        self.current_ba_tick = None
        self.order_num = 0
        self.order_traded = []
        self.status = -1
        self.set_status(tradestatus.BUY_WAIT)

    def get_status(self):
        return self.status

    def set_status(self, status):
        before = self.status
        self.status = status
        if before != self.status:
            logger.info('BUY STATUS %s to %s', tradestatus.status_to_str(before), tradestatus.status_to_str(status))
            if self.get_status() == tradestatus.BUY_CANCEL:
                # consider two cases (1) BUY_CANCEL but TRADED, (2) BUY_CANCEL succeeded
                pass

    def set_order_quantity(self, qty):
        self.quantity = qty

    def get_buy_average(self):
        amount = sum([d['quantity'] * d['price'] for d in self.order_traded])
        quantity = sum([d['quantity'] for d in self.order_traded])
        return amount / quantity, quantity

    def is_done(self, qty):
        if self.quantity == qty:
            return True
        self.quantity -= qty
        return False

    def receive_result(self, result):
        if result['flag'] == '4': # This should be received
            self.order_num = result['order_number']
            if self.quantity == result['quantity']:
                self.set_status(tradestatus.BUY_ORDER_CONFIRM)
            else:
                logger.error("ORDER QUANTITY and flag '4' QUANTITY DIFFERENT, ORDERED %d, RECEIVE %d", self.quantity, result['quantity'])
                self.set_status(tradestatus.BUY_FAIL)
        elif result['flag'] == '1':
            self.order_traded.append(result)
            if self.is_done(result['quantity']):
                self.set_status(tradestatus.BUY_DONE)
            else:
                self.set_status(tradestatus.BUY_SOME)
                    
    def is_abnormal_bid_table(self, bid_table):
        for i in range(len(bid_table)-1):
            distance = price_info.get_price_unit_distance(bid_table[i], bid_table[i+1], self.code_info['is_kospi'])
            if distance > 3:
                return True
        return False

    def ba_data_handler(self, code, data):
        self.current_ba_tick = data
        if self.order_done: #only has one chance
            return

        self.order_done = True

        bid_table = [data['fifth_bid_price'], data['fourth_bid_price'],
                        data['third_bid_price'], data['second_bid_price'],
                        data['first_bid_price']]
        price_table = [(data['first_ask_price'], data['first_ask_remain']),
                        (data['second_ask_price'], data['second_ask_remain']),
                        (data['third_ask_price'], data['third_ask_remain'])]
        price = self.find_target_price(price_table)
        if (price == 0 or
                #self.is_abnormal_bid_table(bid_table) or
                price_info.get_price_unit_distance(data['first_bid_price'], data['first_ask_price'], self.code_info['is_kospi']) > 2):
            logger.warning('STOP, BA price is abnormal or cannot find target price %d\nPRICE TABLE: %s\nBID TABLE: %s\nFIRST BID PRICE %d\nFIRST ASK PRICE %d', price, str(price_table), str(bid_table), data['first_bid_price'], data['first_ask_price'])
            self.set_status(tradestatus.BUY_FAIL)
        else:
            qty = int(self.balance / price)
            if qty > 0:
                #qty = 1
                self.set_order_quantity(qty)
                logger.info('PROCESS BUY ORDER %s, price: %d, qty: %d', code, price, qty)
                result = stock_api.order_stock(self.reader, code, price, qty, True)
                logger.info('BUY ORDER RETURN %s', str(result))
                if result['status'] != 0:
                    self.set_status(tradestatus.BUY_FAIL)
                else:
                    self.set_status(tradestatus.BUY_ORDER_SEND_DONE)
            else:
                logger.warning('QUANTITY is 0, balance: %d, price: %d', self.balance, price)
                self.set_status(tradestatus.BUY_FAIL)

    def tick_handler(self, data):
        pass

    def find_target_price(self, table):
        invest = self.balance
        table_index = -1

        for i, t in enumerate(table):
            if t[0] > invest:
                table_index = i - 1
                break
            elif t[0] * t[1] > invest:
                table_index = i
                break
            else:
                invest -= t[0] * t[1]
            
        if table_index == -1:
            return 0

        return table[table_index][0]
