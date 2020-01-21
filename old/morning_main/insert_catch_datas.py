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
from pymongo import MongoClient
from morning.config import db


def trading():
    # day data insertion: INSERT DAY DATA
    """     INSERT DAY DATA
    from morning.back_data.fetch_stock_data import get_day_period_data

    from_datetime = datetime(2017, 1, 1)
    until_datetime = datetime(2019, 12, 21)
    stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    remote_codes = []
    kospi_codes = list(stock['KOSPI_CODES'].find())
    kosdaq_codes = list(stock['KOSDAQ_CODES'].find())
    codes = []
    codes.extend(kospi_codes)
    codes.extend(kosdaq_codes)
    for code in codes:
        remote_codes.append(code['code'])
    for code in remote_codes:
        get_day_period_data(code, from_datetime.date(), until_datetime.date())
    """
    
    # second phase: INSERT BULL CODE and CODES
    from_datetime = datetime(2018, 1, 1)

    while from_datetime < datetime(2019, 12, 21):
        print('START: ', from_datetime, '-------------------------')
        if is_holidays(from_datetime):
            from_datetime += timedelta(days = 1)
            continue
        
        StockSearchBullChooser(StockSearchBullChooser.KOSDAQ, from_datetime.date(), True)
        StockSearchBullChooser(StockSearchBullChooser.KOSPI, from_datetime.date(), True)
        from_datetime += timedelta(days = 1)
    

    # third phase INSERT MINUTE DATA
    """ INSERT MINUTE DATA by following StockSearchBullChooser
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
    """ 

    print('DONE')
    


if __name__ == '__main__':
    morning_launcher.morning_launcher(True, trading)
