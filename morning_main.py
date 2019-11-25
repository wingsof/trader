import sys
import os
from pymongo import MongoClient
import pymongo
import time
from datetime import datetime, timedelta, date

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

from morning.needle.tick_graph_needle import TickGraphNeedle
from morning.needle.tick_excel_needle import TickExcelNeedle

if __name__ == '__main__':
    start_datetime = datetime(2019, 11, 20)
    traders = []

    fake_account = FakeAccount('account.xlsx')
    while start_datetime < datetime(2019, 11, 21):
        print('START: ', start_datetime, '-------------------------')
        until_datetime = start_datetime + timedelta(days=1)
        if start_datetime.weekday() > 4:
            start_datetime += timedelta(days = 1)
            continue

        fake_account.set_date(start_datetime.date())
        trader = Trader(False)
        traders.append(trader) # For preventing segmentation fault
        if not trader.ready():
            print('Not satisfied conditions', flush=True)
            sys.exit(1)

        tt = TradingTunnel(trader)
        from_datetime = start_datetime
        #tt.set_chooser(KosdaqBullChooser(from_datetime, until_datetime))
        tt.set_chooser(DatabaseOneCodeChooser('A082800', from_datetime, until_datetime))
        decision = BoolAndDecision(2, 1)

        swu = StartWithUp(3)
        stg = TickGraphNeedle()
        ten = TickExcelNeedle()
        stg.filter_codes(['A082800'])
        stg.filter_date(date(2019, 11, 20))
        ten.filter_codes(['A082800'])
        ten.filter_date(date(2019, 11, 20))
        stg.tick_connect(swu)
        ten.tick_connect(swu)

        kosdaq_tick_pipeline = { 'name': 'kosdaq_tick',
                                'stream': DatabaseTick(from_datetime, until_datetime, True, True),
                                'converter': StockTickConverter(),
                                'filter': [InMarketFilter(), DropDataFilter(1)],
                                'strategy': [swu, BuySumTrend()],
                                'decision': decision }

        kosdaq_ba_tick_pipeline = { 'name': 'kosdaq_ba_tick',
                                    'stream': DatabaseBidAskTick(from_datetime, until_datetime, True),
                                    'converter': StockBidAskTickConverter(),
                                    'filter': [],
                                    'strategy': [DeliverBidAsk()],
                                    'decision': decision }

        tt.add_pipeline(kosdaq_tick_pipeline)
        tt.add_pipeline(kosdaq_ba_tick_pipeline)

        trader.add_tunnel(tt)

        trader.set_account(fake_account)
        trader.run()
    
        print('-------------------------', 'DONE')
        stg.process()
        ten.process()
        start_datetime += timedelta(days = 1)

    fake_account.summary()

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
