from datetime import datetime, timedelta
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db
from morning.cybos_api import stock_chart
from morning.back_data.fetch_stock_data import get_day_period_data

class KosdaqBullChooser(Chooser):
    def __init__(self, from_datetime = datetime.now(), until_datetime = datetime.now(), max_count=40):
        super().__init__()
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime
        self.max_count = max_count
        self.mc = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        self.codes = list(self.mc['KOSDAQ_BY_TRADED'].find({'date': {'$gte':from_datetime, '$lte': until_datetime}}))

    def store_daily_data_in_db(self, days=180):
        # deprecated
        #for code in self._get_codes(False):
        #    get_day_period_data(code, self.until_datetime - timedelta(days=days), self.until_datetime)
        pass

    def _get_codes(self, add_prefix=True):
        if len(self.codes):
            codes = self.codes[-1]
            codes.pop('_id', None)
            codes.pop('date', None)
            prefixed_codes = []
            for v in codes.values():
                if add_prefix:
                    prefixed_codes.append('cybos:' + v)
                else:
                    prefixed_codes.append(v)
                if len(prefixed_codes) >= self.max_count:
                    break
            return set(prefixed_codes)
        return set()

    def start(self):
        self.selection_changed.emit(self._get_codes())
