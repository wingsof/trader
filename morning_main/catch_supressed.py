import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from morning.trader import Trader
from morning.trading_tunnel import TradingTunnel
from morning.pipeline.chooser.cybos.db.kosdaq_bull_chooser import KosdaqBullChooser
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.converter.cybos.stock.tick import StockTickConverter
from morning.pipeline.stream.cybos.stock.db.tick import DatabaseTick
from morning.pipeline.filter.in_market import InMarketFilter
from morning.pipeline.filter.drop_data import DropDataFilter
from morning.pipeline.strategy.stock.daily_highest_supressed import DailyHighestSuppressed
from morning.account.day_profit_compare_account import DayProfitCompareAccount


from morning.needle.tick_graph_needle import TickGraphNeedle

from morning_main import morning_launcher


def trading():
    day_profit_compare_account = DayProfitCompareAccount('catch_supressed')
    from_datetime = datetime(2019, 11, 11)

    while from_datetime < datetime(2019, 11, 29):
        print('START: ', from_datetime, '-------------------------')
        until_datetime = from_datetime + timedelta(days=1)
        if from_datetime.weekday() > 4:
            from_datetime += timedelta(days = 1)
            continue

        trader = Trader(False)
        day_profit_compare_account.set_up(0)

        tt = TradingTunnel(trader)
        tt.set_chooser(KosdaqBullChooser(from_datetime, until_datetime, 1))
        dhs = DailyHighestSuppressed()

        pipeline = {'name': 'catch_supressed',
                    'stream': DatabaseTick(from_datetime, until_datetime, True, True),
                    'converter': StockTickConverter(),
                    'filter': [InMarketFilter(), DropDataFilter(1)],
                    'strategy': [dhs],
                    'decision': BoolAndDecision(1, 1)}
        tt.add_pipeline(pipeline)

        trader.add_tunnel(tt)
        trader.set_account(day_profit_compare_account)
        trader.run()
        from_datetime += timedelta(days = 1)

    day_profit_compare_account.summary()


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)