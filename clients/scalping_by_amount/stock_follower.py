from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))

from morning_server import stock_api
from morning.pipeline.converter import dt
from datetime import datetime
from clients.scalping_by_amount import trader

import gevent


class StockFollower:
    STATUS_PRE_MARKET = 0
    STATUS_MARKET = 1
    STATUS_VI = 2
    STATUS_CLOSE_MARKET = 3

    def __init__(self, reader, code, yesterday_summary, is_kospi):
        self.reader = reader
        self.code = code
        self.open_price = 0
        self.yesterday_summary = yesterday_summary
        self.tick_data = []
        self.sec_data = []
        self.current_price = 0
        self.is_kospi = is_kospi
        self.status = StockFollower.STATUS_PRE_MARKET
        self.trader = None

    def start_trading(self, code_info):
        self.trader = trader.Trader(self.reader, code_info)
        stock_api.subscribe_stock(self.reader, self.code + message.BIDASK_SUFFIX, self.trader.ba_tick_handler)


    def is_trading_done(self):
        return self.trader is None

    def tick_data_handler(self, code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        tick_data = dt.cybos_stock_tick_convert(tick_data)
        market_type = tick_data['market_type']
        self.current_price = tick_data['current_price']

        # for drop first IN_MARKET tick
        if self.status == StockFollower.STATUS_MARKET:
            self.tick_data.append(a)

        if self.status == StockFollower.STATUS_PRE_MARKET and market_type == dt.MarketType.IN_MARKET:
            self.status = StockFollower.STATUS_MARKET
            self.open_price = tick_data['current_price']
        elif self.status == StockFollower.STATUS_MARKET and market_type == dt.MarketType.PRE_MARKET_EXP:
            self.status = StockFollower.STATUS_VI
        elif self.status == StockFollower.STATUS_VI and market_type == dt.MarketType.IN_MARKET:
            self.status = StockFollower.STATUS_MARKET

    def subject_handler(self, code, data):
        if len(data) != 1:
            return
        subject_data = data[0]

    def snapshot(self, count_of_sec):
        if len(self.sec_data) == 0:
            return None

        data = self.sec_data[-count_of_sec:]
        current_close = 0
        amount = 0
        if len(self.tick_data):
            current_close = self.tick_data[-1]['current_price']
            amount += sum([d['current_price'] * d['volume'] for d in self.tick_data])
        else:
            current_close = data[-1]['close']

        amount += sum([d['amount'] for d in data])
        profit = (current_close - data[0]['open']) / data[0]['open'] * 100
        yesterday_close = 0
        if self.yesterday_summary is not None:
            yesterday_close = self.yesterday_summary['close_priec']
        return {'code': self.code, 'amount': amount, 'profit': profit,
                'yesterday_close': yesterday_close, 'today_open': self.open_price,
                'current_price': current_close, 'is_kospi': self.is_kospi}

    def process_tick(self):
        # every 1 second this will be called
        if len(self.tick_data) == 0:
            return
        amount = sum([d['current_price'] * d['volume'] for d in self.tick_data])
        self.sec_data.append({'amount': amount,
                            'open': self.tick_data[0]['current_price'],
                            'close': self.tick_data[-1]['current_price']})
        self.tick_data.clear()

    def subscribe_at_startup(self):
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)

