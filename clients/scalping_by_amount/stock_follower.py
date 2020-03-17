from gevent import monkey; monkey.patch_all()

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..' + os.sep] * 2))))
import numpy as np
from configs import client_info
if client_info.TEST_MODE:
    from clients.scalping_by_amount.mock import stock_api
    from clients.scalping_by_amount.mock import datetime
else:
    from morning_server import stock_api
    from datetime import datetime

from morning.pipeline.converter import dt
from clients.scalping_by_amount import trader, price_info
from clients.scalping_by_amount.marketstatus import MarketStatus
from utils import trade_logger as logger

import gevent


class StockFollower:
    READY = 0
    WAIT_BOTTOM_PEAK = 1
    WAIT_OVER_LINE = 2

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
        self.bottom_edges = None
        self.trader = None
        self.status = StockFollower.READY
        self.ba_waching = False
        self.code_info = None
        self.current_price = 0
        self.point_price = 0

    def get_status(self):
        return self.status

    def status_to_str(self, status):
        if status == StockFollower.READY:
            return "READY"
        elif status == StockFollower.WAIT_BOTTOM_PEAK:
            return "WAIT_BOTTOM_PEAK"
        elif status == StockFollower.WAIT_OVER_LINE:
            return "WAIT_OVER_LINE"
        return "UNKNOWN"


    def set_status(self, status):
        if status != self.status:
            logger.info('*%s from %s to %s', self.code, self.status_to_str(self.status), self.status_to_str(status))

        if self.status == StockFollower.WAIT_BOTTOM_PEAK and status == StockFollower.WAIT_OVER_LINE:
            self.trader = trader.Trader(self.reader, self.point_price, self.code_info, self.market_status)
            self.trader.start()
        self.status = status

    def start_trading(self, code_info):
        logger.warning('START TRADING %s', self.code)
        if client_info.TEST_MODE:
            stock_api.set_start_time(self.code)

        self.code_info = code_info
        self.top_edges = list(price_info.get_peaks(self.avg_prices))
        self.bottom_edges = list(price_info.get_peaks(self.avg_prices, False))
        self.point_price = self.current_price
        self.set_status(StockFollower.WAIT_BOTTOM_PEAK)
        if not self.ba_waching:
            self.ba_watching = True
            stock_api.subscribe_stock_bidask(self.reader, self.code, self.ba_data_handler)

    def is_in_market(self):
        return self.market_status.is_in_market()

    def finish_work(self):
        if self.trader is not None:
            self.trader.finish_work()
        self.set_status(StockFollower.READY)

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
                self.set_status(StockFollower.READY)
                self.trader = None

    def tick_data_handler(self, code, data):
        if len(data) != 1:
            return

        tick_data = data[0]
        tick_data = dt.cybos_stock_tick_convert(tick_data)
        has_change = self.market_status.set_tick_data(tick_data)

        self.current_price = tick_data['current_price']
        if self.get_status() == StockFollower.WAIT_BOTTOM_PEAK and self.current_price > self.point_price:
            self.point_price = self.current_price

        # for skipping first tick of in-market data
        if not has_change and self.market_status.is_in_market():
            if self.open_price == 0 and tick_data['start_price'] != 0:
                self.open_price = tick_data['start_price']

            self.tick_data.append(tick_data)
        elif (has_change and not self.market_status.is_in_market() and
                self.get_status() == StockFollower.WAIT_BOTTOM_PEAK):
            self.set_status(StockFollower.READY)

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

        bottom_peaks = list(price_info.get_peaks(self.avg_prices, False))
        if bottom_peaks != self.bottom_edges:
            self.bottom_edges = bottom_peaks
            if self.get_status() == StockFollower.WAIT_BOTTOM_PEAK:
                if self.current_price < self.point_price:
                    self.set_status(StockFollower.WAIT_OVER_LINE)
                else:
                    self.set_status(StockFollower.READY)

        if self.trader is not None:
            peaks = list(price_info.get_peaks(self.avg_prices))
            if peaks != self.top_edges:
                self.top_edges = peaks
                self.trader.top_edge_detected()
            

    def subscribe_at_startup(self):
        stock_api.subscribe_stock(self.reader, self.code, self.tick_data_handler)

