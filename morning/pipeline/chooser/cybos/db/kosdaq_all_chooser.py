from datetime import datetime, timedelta
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db
from utils import time_converter
from morning.back_data.fetch_stock_data import get_day_period_data


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
        codes = self.codes
        self.codes = []
        for code in codes:
            from_date = date - timedelta(days=20)
            data = get_day_period_data(code, from_date, date)

            if len(data) < self.institution_buy_days:
                continue
            
            data = data[-(self.institution_buy_days):]
            remove = False
            for d in data:
                if d['12'] < 0:
                    remove = True
                    break
            
            if not remove:
                self.codes.append(code)

                