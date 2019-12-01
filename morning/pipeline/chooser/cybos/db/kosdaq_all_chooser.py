from datetime import datetime, timedelta
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db
from utils import time_converter


class KosdaqAllChooser(Chooser):
    def __init__(self, institution_buy_days=3):
        super().__init__()
        self.institution_buy_days = institution_buy_days
        self.stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        self.codes = list(self.stock['KOSDAQ_CODES'].find())
        if self.codes.count() == 0:
            from morning.cybos_api.stock_code import get_kosdaq_code_list
            self.codes = get_kosdaq_code_list()
            for code in self.codes:
                self.stock['KOSDAQ_CODES'].insert_one({'code': code})
        
    def set_date(self, date):
        self._filter_consecutive_buy_days(date)

    def start(self):
        self.selection_changed.emit(set(['cybos:'+ code for code in self.codes]))

    def _filter_consecutive_buy_days(self, date):
        for code in self.codes:
            from_date = date - timedelta(days=20)
            db_data = list(self.stock[code + '_D'].find({'0': {'$gte':time_converter.datetime_to_intdate(from_date), 
                                                                '$lte': time_converter.datetime_to_intdate(date)}}))

            if len(db_data) > 3 and time_converter.intdate_to_datetime(db_data[-1]['0']).date() == today:
                