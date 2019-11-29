from datetime import datetime
from pymongo import MongoClient

from morning.pipeline.chooser.chooser import Chooser
from morning.config import db


class KosdaqBullChooser(Chooser):
    def __init__(self, from_datetime = datetime.now(), until_datetime = datetime.now(), max_count=40):
        super().__init__()
        self.max_count = max_count
        mc = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        self.codes = list(mc['KOSDAQ_BY_TRADED'].find({'date': {'$gte':from_datetime, '$lte': until_datetime}}))

    def start(self):
        if len(self.codes):
            codes = self.codes[-1]
            codes.pop('_id', None)
            codes.pop('date', None)
            prefixed_codes = []
            for v in codes.values():
                prefixed_codes.append('cybos:' + v)
                if len(prefixed_codes) >= self.max_count:
                    break
            self.selection_changed.emit(set(prefixed_codes))
