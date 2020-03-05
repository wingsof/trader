from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from datetime import datetime
from clients.scalping_by_amount import tradestatus

import gevent


class BuyStage:
    def __init__(self, reader, market_status, balance):
        self.reader = reader
        self.balance = balance
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
            print('*' * 10, 'BUY STATUS', tradestatus.status_to_str(before), 'TO', tradestatus.status_to_str(status), '*' * 10)
            if self.get_status() == tradestatus.BUY_CANCEL:
                # consider two cases (1) BUY_CANCEL but TRADED, (2) BUY_CANCEL succeeded
                pass

    def set_order_quantity(self, qty):
        self.quantity = 0

    def get_buy_average(self):
        amount = ([d['quantity'] * d['price'] for d in self.order_traded])
        quantity = sum([d['quantity'] for d in self.order_traded])
        return amount / quantity, quantity

    def is_done(self, qty):
        if self.quantity == qty:
            return True
        self.quantity -= qty
        return False

    def receive_result(self, result):
        if result['flag'] == 4: # This should be received
            self.order_num = result['order_number']
            if self.quantity == result['quantity']:
                self.set_status(tradestatus.BUY_ORDER_CONFIRM)
            else:
                print('cannot be possible')
                self.set_status(tradestatus.BUY_FAIL)
        elif result['flag'] == 1:
            self.order_traded.append(result)
            if self.is_done(result['quantity']):
                self.set_status(tradestatus.BUY_DONE)
            else:
                self.set_status(tradestatus.BUY_SOME)
                    

    def ba_data_handler(self, code, data):
        self.current_ba_tick = data
        if self.order_done: #only has one chance
            return

        self.order_done = True

        price_table = [(tick_data['first_ask_price'], tick_data['first_ask_remain']),
                        (tick_data['second_ask_price'], tick_data['second_ask_remain']),
                        (tick_data['third_ask_price'], tick_data['third_ask_remain'])]
        price = self.find_target_price(price_table)
        if price == 0:
            print('stop, cannot find target price', price_table)
            self.set_status(tradestatus.BUY_FAIL)
        else:
            qty = int(self.balance / price)
            if qty > 0:
                #TODO: change real qty after testing done
                self.set_order_quantity(1)
                print('*' * 20, 'process buy order', code, 'price:', price, 'qty:', qty, '*' * 20)
                result = stock_api.order_stock(self.reader, code, price, qty, True)
                print('*' * 20, '\nBUY ORDER RETURN\n', result, '*' * 20)
                if result['status'] != 0:
                    self.set_status(tradestatus.BUY_FAIL)
                else:
                    self.set_status(tradestatus.BUY_ORDER_SEND_DONE)
            else:
                print('quantity wrong', 'balance', self.balance, 'price', price)
                self.set_status(tradestatus.BUY_FAIL)

    def tick_handler(self, data):
        pass

    def find_target_price(self, table):
        invest = self.invest_balance
        table_index = -1
        for i, t in enumerate(table):
            invest -= t[0] * t[1] 
            if invest < 0:
                table_index = i
                break
        if table_index == -1:
            return 0

        return table[table_index][0]
