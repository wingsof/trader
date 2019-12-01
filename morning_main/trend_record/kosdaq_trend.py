import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))

from pymongo import MongoClient
import pandas as pd
from morning.cybos_api import stock_chart
from morning.config import db
from datetime import datetime, timedelta
from utils import time_converter

class KosdaqTrend:
    def __init__(self, today):        
        while today.weekday() > 4:# TODO record holidays
            today -= timedelta(days=1)

        from_date = today - timedelta(days=365)

        code = 'KOSDAQ'
        self.df = None
        stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        db_data = list(stock_db[code + '_D'].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), 
                                                   '$lte': time_converter.datetime_to_intdate(today)}}))
        
        # TODO: how to validate? and there is an error when today is holiday
        if len(db_data) > 200 and time_converter.intdate_to_datetime(db_data[-1]['0']).date() == today:
            self.df = pd.DataFrame(db_data)
            print('found from db', len(self.df))
        else:
            last_record = time_converter.intdate_to_datetime(db_data[-1]['0']).date() + timedelta(days=1) if len(db_data) > 0 else from_date
            length, data = stock_chart.get_day_period_data('U201', last_record, today)
            if length > 0:
                stock_db['KOSDAQ_D'].insert_many(data)
            self.df = pd.DataFrame(data)

    def current_greater_than_mean(self, days=20):
        prices = self.df['5'].rolling(days).mean()
        return prices.iloc[-1] < self.df['5'].iloc[-1]
    