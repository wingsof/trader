# Using minute data and check condition in Kosdaq Market





import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from morning.trader import Trader
from morning.trading_tunnel import TradingTunnel
from morning.pipeline.chooser.cybos.db.kosdaq_all_chooser import KosdaqAllChooser
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.converter.cybos.stock.day_tick import StockDayTickConverter
from morning.pipeline.stream.cybos.stock.db.min_tick import MinTick
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.strategy.stock.daily_highest_supressed import DailyHighestSuppressed
from morning.account.day_profit_compare_account import DayProfitCompareAccount
from morning_main.kosdaq_trend import KosdaqTrend

from morning.needle.tick_graph_needle import TickGraphNeedle

from morning_main import morning_launcher
from morning.needle.tick_graph_needle import TickGraphNeedle


def trading():
    day_profit_compare_account = DayProfitCompareAccount('catch_kosdaq_supressed')
    from_datetime = datetime(2018, 1, 1)

    while from_datetime < datetime(2019, 11, 29):
        print('START: ', from_datetime, '-------------------------')
        if from_datetime.weekday() > 4:
            from_datetime += timedelta(days = 1)
            continue
        # TODO: Consider holidays for long period testing
        
        kt = KosdaqTrend(from_datetime)
        if not kt.current_greater_than_mean():
            from_datetime += timedelta(days = 1)
            continue

        trader = Trader(False)
        day_profit_compare_account.set_up(0)

        tt = TradingTunnel(trader)
        kac = KosdaqAllChooser()
        kac.set_date(from_datetime)

        tt.set_chooser(kac)
        #dhs = DailyHighestSuppressed(5)
        
        pipeline = {'name': 'catch_kosdaq_supressed',
                    'stream': MinTick(from_datetime, True),
                    'converter': StockDayTickConverter(),
                    'filter': [],
                    'strategy': [],
                    'decision': BoolAndDecision(1, 1)}
        tt.add_pipeline(pipeline)

        trader.add_tunnel(tt)
        trader.set_account(day_profit_compare_account)
        trader.run()
        from_datetime += timedelta(days = 1)

    day_profit_compare_account.summary()


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)