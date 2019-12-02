import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))

from pymongo import MongoClient
import pandas as pd
from morning.cybos_api import stock_chart
from morning.config import db
from datetime import datetime, timedelta
from morning.back_data import fetch_stock_data
from utils import time_converter

class KosdaqTrend:
    def __init__(self, today):        
        from_date = today - timedelta(days=365)
        data = fetch_stock_data.get_day_period_data('U201', from_date, today)
        self.df = pd.DataFrame(data)

    def current_greater_than_mean(self, days=20):
        prices = self.df['5'].rolling(days).mean()
        return prices.iloc[-1] < self.df['5'].iloc[-1]
    