import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))

from pymongo import MongoClient
import pandas as pd
from morning.config import db
from datetime import datetime, timedelta, date
from morning.back_data import fetch_stock_data
from utils import time_converter
from morning.back_data.holidays import get_yesterday

class KosdaqTrend:
    def __init__(self, today: date):
        if not isinstance(today, date):
            raise TypeError('today is not instance of date')

        from_date = today - timedelta(days=365)
        data = fetch_stock_data.get_day_period_data('U201', from_date, get_yesterday(today))
        data = sorted(data, key = lambda i: i['0']) 

        self.df = pd.DataFrame(data)

    def current_greater_than_mean(self, days=20):
        prices = self.df['5'].rolling(days).mean()
        print('KosdaqTrend', '20 mean',  prices.iloc[-1], 'today', self.df['5'].iloc[-1])
        return prices.iloc[-1] < self.df['5'].iloc[-1]

    def get_yesterday_index(self):
        return self.df['5'].iloc[-1]

    def get_yesterday_ma(self):
        prices = self.df['5'].rolling(20).mean()
        return prices.iloc[-1]
