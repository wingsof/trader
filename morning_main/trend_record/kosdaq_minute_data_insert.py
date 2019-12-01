import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))

from morning.cybos_api.stock_chart import get_min_period_data
from morning.cybos_api.stock_code import get_kosdaq_code_list
from morning.config import db

from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
from utils import time_converter

class KosdaqMinuteDataInsert:
    def __init__(self, today):
        while today.weekday() > 4: # TODO record holidays
            today -= timedelta(days=1)
            from_date = today - timedelta(days=360)

        stock_db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        for code in get_kosdaq_code_list():
            db_data = list(stock_db[code + '_M'].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), 
                                                    '$lte': time_converter.datetime_to_intdate(today)}}))

            if len(db_data) > 0 and time_converter.intdate_to_datetime(db_data[-1]['0']).date() == today:
                print('found')
            else:
                last_record = time_converter.intdate_to_datetime(db_data[-1]['0']).date()  + timedelta(days=1) if len(db_data) > 0 else from_date
                length, data = get_min_period_data(code, last_record, today)
                if length > 0:
                    stock_db[code + '_M'].insert_many(data)


        """
        l, data = stock_chart.get_day_period_data(code, self.until_datetime - timedelta(days=days), self.until_datetime)
            if l > 0:
                self.mc[code + '_D'].drop()
                self.mc[code + '_D'].insert_many(data)
            else:
                print('No Data')
        """


#kmdi = KosdaqMinuteDataInsert(datetime.now())
