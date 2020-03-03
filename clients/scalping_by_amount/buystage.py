from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime

import gevent


class BuyStage:
    def __init__(self, reader, market_status, callback, balance):
        self.reader = reader
        self.balance = balance
        self.interrupt_callback = callback
        self.market_status = market_status
        self.quantity = 0
        self.order_done = False
        self.current_ba_tick = None
        self.order_num = 0
        self.order_traded = []

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

    def confirm_result(self):
        gevent.sleep(10)
        print('confirm result quantity remained', self.quantity)

    def process_result(self, result):
        if 'flag' not in result or 'quantity' not in result:
            print('result something wrong', result)
            return

        is_done = False
        if result['flag'] == 4: # This should be received
            self.order_num = result['order_number']
            if self.quantity == result['quantity']:
                print('goes well')
                gevent.spawn(self.confirm_result)
            else:
                print('something wrong')
        elif result['flag'] == 1:
            is_done = self.is_done(result['quantity'])
            self.order_traded.append(result)
        
        return is_done

    def ba_data_handler(self, code, data):
        self.current_ba_tick = data
        if self.order_done:
            return

        self.order_done = True

        price_table = [(tick_data['first_ask_price'], tick_data['first_ask_remain']),
                        (tick_data['second_ask_price'], tick_data['second_ask_remain']),
                        (tick_data['third_ask_price'], tick_data['third_ask_remain'])]
        price = self.find_target_price(price_table)
        if price == 0:
            print('stop, cannot find target price', price_table)
            self.interrupt_callback()
        else:
            qty = int(self.balance / price)
            if qty > 0:
                self.set_order_quantity(qty)
                result = stock_api.order_stock(self.reader, code, price, qty, True)
                print('order return', result)
                if result['status'] != 0:
                    print('something wrong')

            else:
                print('quantity wrong', 'balance', self.balance, 'price', price)
                self.interrupt_callback()


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

