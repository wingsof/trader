# Using minute data and check condition in Kosdaq Market
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from morning.trader import Trader
from morning.pipeline.decision.bool_and_decision import BoolAndDecision
from morning.pipeline.converter.cybos.stock.day_tick import StockDayTickConverter
from morning.pipeline.stream.cybos.stock.db.min_tick import MinTick
from morning.pipeline.chooser.cybos.db.stock_search_bull_chooser import StockSearchBullChooser
from morning.account.fake_account import FakeAccount
from morning_main.trend_record.kospi_trend import KospiTrend
from morning.pipeline.strategy.stock.minute_suppressed import MinuteSuppressed

from morning.needle.tick_graph_needle import TickGraphNeedle

from morning_main import morning_launcher
from morning.back_data.holidays import is_holidays

from PyQt5.QtCore import QEventLoop
import platform


clients_count = 0
loop = None

def decrement_thread_count():
    global clients_count
    clients_count -= 1
    print('COUNT', clients_count)
    if clients_count == 0:
        loop.quit()


def trading():
    global clients_count
    global loop

    fake_account = FakeAccount('catch_kosdaq_supressed')
    from_datetime = datetime(2019, 12, 20)


    while from_datetime < datetime(2019, 12, 21):
        loop = QEventLoop()
        traders = []
        print('START: ', from_datetime, '-------------------------')
        if is_holidays(from_datetime):
            from_datetime += timedelta(days = 1)
            continue
        
        kt = KospiTrend(from_datetime.date())

        fake_account.clear_additional_info()
        fake_account.add_additional_info('yesterday_kospi', kt.get_yesterday_index())
        fake_account.add_additional_info('yesterday_ma', kt.get_yesterday_ma())
        ksbc = StockSearchBullChooser(StockSearchBullChooser.KOSPI, from_datetime.date(), True)

        fake_account.set_date(from_datetime.date())
        clients_count = len(ksbc.codes)
        for code in ksbc.codes:
            if platform.system() == 'Windows':
                from morning.back_data.fetch_stock_data import get_day_minute_period_data
                get_day_minute_period_data(code, from_datetime.date(), from_datetime.date())
            trader = Trader(code, True)
            traders.append(trader) 
            pipeline = {'name': 'catch_kosdaq_supressed',
                        'stream': MinTick(from_datetime.date(), True),
                        'converter': StockDayTickConverter(),
                        'filter': [],
                        'strategy': [MinuteSuppressed()],
                        'decision': BoolAndDecision(1, 1)}
            trader.add_pipeline(pipeline)
            trader.set_account(fake_account)
            trader.finished.connect(decrement_thread_count)
            trader.start_trading()

        loop.exec()
        traders.clear()
        from_datetime += timedelta(days = 1)

    fake_account.summary()
    



if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)
    from_datetime = datetime(2018, 1, 1)

