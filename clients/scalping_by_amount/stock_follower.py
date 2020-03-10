from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
import numpy as np
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount import mock_stock_api as stock_api

else:
    from morning_server import stock_api

from morning.pipeline.converter import dt
from datetime import datetime
from clients.scalping_by_amount import trader, price_info
from clients.scalping_by_amount.marketstatus import MarketStatus

import gevent


class StockFollower:
    def __init__(self, reader, code, yesterday_summary, is_kospi):
        self.reader = reader
        self.code = code
        self.open_price = 0
        self.yesterday_summary = yesterday_summary
        self.tick_data = []
        self.sec_data = []
        self.is_kospi = is_kospi
        self.market_status = MarketStatus()
        self.avg_prices = []
        self.top_edges = None
        self.trader = None
        self.ba_waching = False

    def start_trading(self, code_info):
        print('*' * 10, 'START TRADING', self.code, '*' * 10)
        self.trader = trader.Trader(self.reader, code_info, self.market_status)
        self.top_edges = list(price_info.get_peaks(self.avg_prices))
        if not self.ba_waching:
            self.ba_watching = True
            stock_api.subscribe_stock_bidask(self.reader, self.code, self.ba_data_handler)
        self.trader.start()

    def is_in_market(self):
        return self.market_status.is_in_market()

    def receive_result(self, result):
        if self.trader is not None:
            self.trader.receive_result(result)

    def is_trading_done(self):
        if self.trader is None:
            return True
        return False

    def ba_data_handler(self, code, data):
        # Use ba data tick as heartbeat for trading
        if len(data) != 1:
            return

        tick_data = data[0]
        tick_data = dt.cybos_stock_ba_tick_convert(tick_data)
        if self.trader is not None:
            # careful not to use code since it has _BA suffix
            self.trader.ba_data_handler(self.code, tick_data)
            if self.trader.is_finished():
                self.trader = None


    def tick_data_handler(self, code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        tick_data = dt.cybos_stock_tick_convert(tick_data)
        has_change = self.market_status.set_tick_data(tick_data)

        # for skipping first tick of in-market data
        if not has_change and self.market_status.is_in_market():
            if self.open_price == 0 and tick_data['start_price'] != 0:
                self.open_price = tick_data['start_price']

            self.tick_data.append(tick_data)

        if self.trader is not None:
            self.trader.tick_data_handler(tick_data)

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
            yesterday_close = self.yesterday_summary['close_price']
        return {'code': self.code, 'amount': amount, 'profit': profit,
                'yesterday_close': yesterday_close, 'today_open': self.open_price,
                'current_price': current_close, 'is_kospi': self.is_kospi}

    def process_tick(self):
        # every 1 second this will be called
        if len(self.tick_data) == 0:
            return
        amount = sum([d['current_price'] * d['volume'] for d in self.tick_data])
        avg_price = np.array([d['current_price'] for d in self.tick_data]).mean()
        self.sec_data.append({'amount': amount,
                            'open': self.tick_data[0]['current_price'],
                            'close': self.tick_data[-1]['current_price'],
                            'date': datetime.now()})
        self.avg_prices.append(avg_price)
        self.tick_data.clear()
        if self.trader is not None:
            peaks = list(price_info.get_peaks(self.avg_prices))
            print('peaks', peaks, type(peaks), 'top_edge', self.top_edges)
            if peaks != self.top_edges:
                self.top_edges = peaks
                self.trader.top_edge_detected()

    def subscribe_at_startup(self):
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)

