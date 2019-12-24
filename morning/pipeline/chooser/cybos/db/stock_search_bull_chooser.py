from datetime import datetime, timedelta, date
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db
from morning.back_data.fetch_stock_data import get_day_period_data
from morning.back_data.holidays import is_holidays, get_yesterday


class StockSearchBullChooser(Chooser):
    KOSPI=1
    KOSDAQ=2

    def __init__(self, market, d: date, use_db=False, institution_buy_days=0, max_count=80):
        super().__init__()
        while is_holidays(d):
            d -= timedelta(days = 1)

        self.from_date = d
        self.max_count = max_count if max_count > 80 else 80
        self.institution_buy_days = institution_buy_days
        self.stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        self.codes = []
        remote_codes = []

        self.code_collection_name = 'KOSPI_CODES' if market == StockSearchBullChooser.KOSPI else 'KOSDAQ_CODES'
        self.code_bull_name = 'KOSPI_BULL' if market == StockSearchBullChooser.KOSPI else 'KOSDAQ_BULL'

        if use_db:
            codes = list(self.stock[self.code_collection_name].find())
            for code in codes:
                remote_codes.append(code['code'])
        print('remote db', len(remote_codes))
        if len(remote_codes) == 0:
            from morning.cybos_api.stock_code import get_kosdaq_company_code_list, get_kospi_company_code_list
            if market == StockSearchBullChooser.KOSPI:
                remote_codes = get_kospi_company_code_list()
            else:
                remote_codes = get_kosdaq_company_code_list()
            for code in remote_codes:
                self.stock[self.code_collection_name].insert_one({'code': code})
        self._search_day_data(remote_codes)

    def _search_from_database(self, search_day, max_count, institution_buy_days):
        bulls = list(self.stock[self.code_bull_name].find({
                                        'date': {'$eq': datetime(search_day.year, search_day.month, search_day.day)}, 
                                        'count': {'$eq': max_count},
                                        'institution_buy_days': {'$eq': institution_buy_days}}))
        print('DB BULL len', len(bulls))
        if len(bulls) > 0:
            print('found from DB')
            bull = bulls[0]
            codes = []
            for i in range(max_count):
                codes.append(bull[str(i)])
            return codes

        return []

    def _search_day_data(self, codes):
        yesterday = get_yesterday(self.from_date)
        print('yesterday', yesterday)
        self.codes = self._search_from_database(yesterday, self.max_count, self.institution_buy_days)
        if len(self.codes):
            print('found pass')
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
            db_insert_data = {'date': datetime(yesterday.year, yesterday.month, yesterday.day), 'count': self.max_count, 
                            'institution_buy_days': self.institution_buy_days}
            for i, code in enumerate(self.codes):
                db_insert_data[str(i)] = code
            self.stock[self.code_bull_name].insert_one(db_insert_data)
            print('OK insert')

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
                