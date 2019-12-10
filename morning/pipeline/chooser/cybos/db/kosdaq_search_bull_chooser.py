from datetime import datetime, timedelta, date
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db
from morning.back_data.fetch_stock_data import get_day_period_data
from morning.back_data.holidays import is_holidays, get_yesterday


class KosdaqSearchBullChooser(Chooser):
    def __init__(self, d: date, institution_buy_days=0, max_count=40):
        super().__init__()
        while is_holidays(d):
            d -= timedelta(days = 1)
        
        self.from_date = d
        self.max_count = max_count
        self.institution_buy_days = institution_buy_days
        self.stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        self.codes = []
        remote_codes = []
        codes = list(self.stock['KOSDAQ_CODES'].find())
        for code in codes:
            remote_codes.append(code['code'])

        if len(remote_codes) == 0:
            from morning.cybos_api.stock_code import get_kosdaq_code_list
            remote_codes = get_kosdaq_code_list()
            for code in remote_codes:
                self.stock['KOSDAQ_CODES'].insert_one({'code': code})
        self._search_day_data(remote_codes)

    def _search_from_database(self, search_day, max_count, institution_buy_days):
        bulls = list(self.stock['KOSDAQ_BULL'].find({
                                        'date': {'$eq': search_day}, 
                                        'count': {'$eq': max_count},
                                        'institution_buy_days': {'$eq': institution_buy_days}}))
        if len(bulls) > 0:
            bull = bulls[0]
            codes = []
            for i in range(max_count):
                codes.append(bull[str(i)])
            return codes

        return []

    def _search_day_data(self, codes):
        yesterday = get_yesterday(self.from_date)
        self.codes = self._search_from_database(yesterday, self.max_count, self.institution_buy_days)
        if len(self.codes):
            pass
        else:
            datas = []
            for code in codes:
                data = get_day_period_data(code, yesterday, yesterday)
                if len(data) > 0:
                    data[0]['code'] = code
                    datas.append(data[0])

            datas = sorted(datas, key=lambda i: i['7'], reverse=True)
            self.codes = [d['code'] for d in datas]
            if self.institution_buy_days > 0:
                self._filter_consecutive_buy_days(yesterday)

            self.codes = self.codes[:self.max_count]
            db_insert_data = {'date': yesterday, 'count': self.max_count, 
                            'institution_buy_days': self.institution_buy_days}
            for i, code in enumerate(self.codes):
                db_insert_data[str(i)] = code
            self.stock['KOSDAQ_BULL'].insert_one(db_insert_data)

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
            if all([d['12'] > 0 for d in data]):
                self.codes.append(code)
                