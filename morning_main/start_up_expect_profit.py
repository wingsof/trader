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
from morning.pipeline.strategy.stock.start_with_up import StartWithUp
from morning.account.day_profit_compare_account import DayProfitCompareAccount

from morning.needle.tick_excel_needle import TickExcelNeedle

from morning_main import morning_launcher

def trading():
    day_profit_compare_account = DayProfitCompareAccount('start_up')

    for up_tick in [2]:
        from_datetime = datetime(2019, 11, 22)

        while from_datetime < datetime(2019, 11, 23):
            print('START: ', up_tick, from_datetime, '-------------------------')
            
            until_datetime = from_datetime + timedelta(days=1)
            if from_datetime.weekday() > 4:
                from_datetime += timedelta(days = 1)
                continue

            trader = Trader(False)
            day_profit_compare_account.set_up(up_tick)

            tt = TradingTunnel(trader)
            tt.set_chooser(KosdaqBullChooser(from_datetime, until_datetime))
            swu = StartWithUp(up_tick)
            ten = TickExcelNeedle()
            ten.tick_connect(swu)
            start_up_profit_pipeline = { 'name': 'start_up_profit',
                                    'stream': DatabaseTick(from_datetime, until_datetime, True, True),
                                    'converter': StockTickConverter(),
                                    'filter': [InMarketFilter(), DropDataFilter(1)],
                                    'strategy': [swu],
                                    'decision':  BoolAndDecision(1, 1) }
            tt.add_pipeline(start_up_profit_pipeline)

            trader.add_tunnel(tt)

            trader.set_account(day_profit_compare_account)
            trader.run()
            from_datetime += timedelta(days = 1)

    day_profit_compare_account.summary()


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)
