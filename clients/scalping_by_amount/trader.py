from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime
from clients.scalping_by_amount import price_info

import gevent


class Trader:
    STATUS_NONE = 0
    def __init__(self, reader, code_info):
        self.reader = reader
        self.target_price = 0
        self.code_info = code_info
        self.balance = stock_api.get_balance(self.reader)
        self.invest_balance = int(self.balance / 10)
        """
        return {'code': self.code, 'amount': amount, 'profit': profit,
                'yesterday_close': yesterday_close, 'today_open': self.open_price,
                'current_price': current_close, 'is_kospi': self.is_kospi}
        """

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

    def ba_data_handler(self. code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        tick_data = dt.cybos_stock_ba_tick_convert(tick_data)

        if self.target_price = 0:
            price_table = [(tick_data['first_ask_price'], tick_data['first_ask_remain']),
                            (tick_data['second_ask_price'], tick_data['second_ask_remain']),
                            (tick_data['third_ask_price'], tick_Data['third_ask_remain'])]
            price = self.find_target_price(price_table)
            if price == 0:
                print('Stop, bid ask is strange', price_table)
                return # TODO: handle stop trading

