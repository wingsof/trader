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
from morning.pipeline.decision.profit_decision import ProfitDecision
from morning.account.day_profit_compare_account import DayProfitCompareAccount
from morning.cybos_api import stock_chart

from datetime import datetime, timedelta, date
from pymongo import MongoClient
from morning.config import db

fetch_cybos = False
start_date = datetime(2019, 1, 1)
end_date = datetime.now()
bull_chooser_date = datetime(2019, 11, 25)

def trading():
    day_profit_compare_account = DayProfitCompareAccount('start_price_effect')

    for inverse in [0, 1]:
        trader = Trader(False)

        # TODO: Fix fake date
        day_profit_compare_account.set_up(inverse)
        tt = TradingTunnel(trader)
        
        
        tt.set_chooser(KosdaqBullChooser(bull_chooser_date, datetime.now()))

        pipeline = {'name': 'start_price_effect',
                    'stream': DayTick(start_date, end_date),
                    'converter': StockDayTickConverter(),
                    'filter': [],
                    'strategy': [YdayCloseTodayStart(bool(inverse))],
                    'decision': ProfitDecision()}
        tt.add_pipeline(pipeline)

        trader.add_tunnel(tt)
        trader.set_account(day_profit_compare_account)
        trader.run()
    day_profit_compare_account.summary()

if __name__ == '__main__':
    if fetch_cybos:
        kbc = KosdaqBullChooser(bull_chooser_date, datetime.now())
        codes = kbc.codes[-1]
        codes.pop('_id', None)
        codes.pop('date', None)
        client = MongoClient(db.HOME_MONGO_ADDRESS)
        for code in codes.values():
            _, data = stock_chart.get_day_period_data(code, start_date, end_date)
            client.stock[code + '_D'].drop()
            client.stock[code + '_D'].insert_many(data)
    
    morning_launcher.morning_launcher(True, trading)