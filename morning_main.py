import sys
import os
from pymongo import MongoClient
import pymongo
import time
import logging
from datetime import datetime

from morning.logging import logger
from morning.trader import Trader
from morning.trading_tunnel import TradingTunnel

from morning.pipeline.chooser.cybos.db.kosdaq_bull_chooser import KosdaqBullChooser
from morning.pipeline.chooser.cybos.db.one_code_chooser import DatabaseOneCodeChooser

from morning.pipeline.stream.cybos.stock.db.tick import DatabaseTick
from morning.pipeline.stream.cybos.stock.db.bidask_tick import DatabaseBidAskTick

from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.converter.cybos.stock.bidask import StockBidAskTickConverter

from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter

from morning.pipeline.strategy.stock.start_with_up import StartWithUp
from morning.pipeline.strategy.stock.buy_sum_trend import BuySumTrend
from morning.pipeline.strategy.stock.bidask.buy_sum_trend import BidAskBuySumTrend
from morning.pipeline.strategy.stock.bidask.deliver_bidask import DeliverBidAsk

from morning.pipeline.decision.bool_and_decision import BoolAndDecision

from morning.account.fake_account import FakeAccount


if __name__ == '__main__':
    logger.setup_main_log()
    trader = Trader(False)

    if not trader.ready():
        print('Not satisfied conditions', flush=True)
        sys.exit(1)

    tt = TradingTunnel(trader)
    from_datetime = datetime(2019, 11, 21)
    until_datetime = datetime(2019, 11, 22)
    tt.set_chooser(KosdaqBullChooser(from_datetime, until_datetime))

    decision = BoolAndDecision(2, 1)
    kosdaq_tick_pipeline = {
            'name': 'kosdaq_tick',
            'stream': DatabaseTick(from_datetime, until_datetime, True, True),
            'converter': StockTickConverter(),
            'filter': [InMarketFilter(), DropDataFilter(1)],
            'strategy': [StartWithUp(3), BuySumTrend()],
            'decision': decision,
    }

    
    kosdaq_ba_tick_pipeline = {
            'name': 'kosdaq_ba_tick',
            'stream': DatabaseBidAskTick(from_datetime, until_datetime, True),
            'converter': StockBidAskTickConverter(),
            'filter': [],
            'strategy': [DeliverBidAsk()],
            'decision': decision,
    }
    
    tt.add_pipeline(kosdaq_tick_pipeline)
    tt.add_pipeline(kosdaq_ba_tick_pipeline)

    trader.add_tunnel(tt)

    trader.set_account(FakeAccount())
    trader.run()
    """
    usecase2 = {
            'name': 'stock_tick',
            'stream': TickRealtime(),
            'converter': TickRealtimeConverter(),
            'filter': [InMarket()],
            'strategy': [pair],
    }

    usecase2_1 = {
            'name': 'stock_tick',
            'stream': TickRealtime(),
            'converter': TickRealtimeConverter(),
            'filter': [InMarket()],
            'strategy': [pair],
    }

    usecase3 = {
            'name': 'stock_tick',
            'stream': TickRealtime(),
            'converter': TickRealtimeConverter(),
            'filter': [InMarket()],
            'strategy': [UpTrend(), BuyTrend()],
    }

    usecase3_1 = {
            'name': 'stock_ba_tick',
            'stream': TickBaRealtime(),
            'converter': TickBaRealtimeConverter(),
            'filter': [InMarket()],
            'strategy': [BaUpTrend()],
    }

    """   
