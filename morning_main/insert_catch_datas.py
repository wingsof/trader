# Using minute data and check condition in Kosdaq Market
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from morning.pipeline.chooser.cybos.db.stock_search_bull_chooser import StockSearchBullChooser
from morning_main import morning_launcher
from morning.back_data.holidays import is_holidays

from PyQt5.QtCore import QEventLoop
import platform



def trading():
    # first phase
    """
    from_datetime = datetime(2018, 1, 1)

    while from_datetime < datetime(2019, 12, 21):
        print('START: ', from_datetime, '-------------------------')
        if is_holidays(from_datetime):
            from_datetime += timedelta(days = 1)
            continue
        
        StockSearchBullChooser(StockSearchBullChooser.KOSDAQ, from_datetime.date(), True)
        StockSearchBullChooser(StockSearchBullChooser.KOSPI, from_datetime.date(), True)
        from_datetime += timedelta(days = 1)
    """
    # second phase
    from_datetime = datetime(2018, 5, 29)

    while from_datetime < datetime(2019, 12, 21):
        print('START: ', from_datetime, '-------------------------')
        if is_holidays(from_datetime):
            from_datetime += timedelta(days = 1)
            continue
        
        ssbc_kospi = StockSearchBullChooser(StockSearchBullChooser.KOSDAQ, from_datetime.date(), True)
        ssbc_kosdaq = StockSearchBullChooser(StockSearchBullChooser.KOSPI, from_datetime.date(), True)
        from morning.back_data.fetch_stock_data import get_day_minute_period_data
        
        for code in ssbc_kospi.codes:
            get_day_minute_period_data(code, from_datetime.date(), (from_datetime + timedelta(days=3)).date())

        for code in ssbc_kosdaq.codes:
            get_day_minute_period_data(code, from_datetime.date(), (from_datetime + timedelta(days=3)).date())

        from_datetime += timedelta(days = 1)


    print('DONE')
    


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)
