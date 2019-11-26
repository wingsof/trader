import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from morning.trader import Trader
from morning.trading_tunnel import TradingTunnel
from morning.pipeline.stream.cybos.stock.db.day_tick import DayTick
from morning_main import morning_launcher
from morning.pipeline.chooser.cybos.db.kosdaq_bull_chooser import KosdaqBullChooser
from morning.pipeline.strategy.stock.yday_close_today_start import YdayCloseTodayStart
from morning.pipeline.converter.cybos.stock.day_tick import StockDayTickConverter
from morning.pipeline.decision.bool_and_decision import BoolAndDecision

from datetime import datetime, timedelta, date


def trading():
    trader = Trader(False)
    tt = TradingTunnel(trader)
    tt.set_chooser(KosdaqBullChooser(datetime(2019, 11, 11), datetime.now()))

    pipeline = {'name': 'start_price_effect',
                'stream': DayTick(datetime(2019, 1, 1), datetime.now(), True),
                'converter': StockDayTickConverter(),
                'filter': [],
                'strategy': YdayCloseTodayStart(True),
                'decision': BoolAndDecision(1, 1)}
    tt.add_pipeline(pipeline)

    trader.add_tunnel(tt)
    trader.run()


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)
