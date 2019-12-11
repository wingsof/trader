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
from morning.pipeline.chooser.cybos.db.kosdaq_search_bull_chooser import KosdaqSearchBullChooser
from morning.pipeline.strategy.stock.daily_highest_supressed import DailyHighestSuppressed
from morning.account.fake_account import FakeAccount
from morning_main.trend_record.kosdaq_trend import KosdaqTrend
from morning.pipeline.strategy.stock.minute_suppressed import MinuteSuppressed

from morning.needle.tick_graph_needle import TickGraphNeedle

from morning_main import morning_launcher
from morning.back_data.holidays import is_holidays

from morning.back_data import fetch_stock_data

def trading():
    fake_account = FakeAccount('catch_kosdaq_supressed')
    from_datetime = datetime(2018, 1, 1)

    while from_datetime < datetime(2019, 12, 11):
        print('START: ', from_datetime, '-------------------------')
        if is_holidays(from_datetime):
            from_datetime += timedelta(days = 1)
            continue
        
        kt = KosdaqTrend(from_datetime.date())
        """
        if not kt.current_greater_than_mean():
            from_datetime += timedelta(days = 1)
            continue
        """
        fake_account.clear_additional_info()
        fake_account.add_additional_info('yesterday_kosdaq', kt.get_yesterday_index())
        fake_account.add_additional_info('yesterday_ma', kt.get_yesterday_ma())
        trader = Trader(False)
        fake_account.set_date(from_datetime.date())
        tt = TradingTunnel(trader)
        ksbc = KosdaqSearchBullChooser(from_datetime.date())
        for code in ksbc.codes:
            fetch_stock_data.get_day_minute_period_data(code, from_datetime.date(), from_datetime.date())
        tt.set_chooser(ksbc)
        
        pipeline = {'name': 'catch_kosdaq_supressed',
                    'stream': MinTick(from_datetime.date(), True),
                    'converter': StockDayTickConverter(),
                    'filter': [],
                    'strategy': [MinuteSuppressed()],
                    'decision': BoolAndDecision(1, 1)}
        tt.add_pipeline(pipeline)

        trader.add_tunnel(tt)
        trader.set_account(fake_account)
        trader.run()
        from_datetime += timedelta(days = 1)

    fake_account.summary()


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)