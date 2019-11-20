from pymongo import MongoClient
from morning.config import db


class DatabaseBidAskTick:
    def __init__(self, from_datetime, until_datetime, is_main_clock = False):
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime
        self.is_main_clock = is_main_clock

    def set_target(self, code):
        db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        
        cursor = db[code + '_BA'].find({'date': {'$gte':self.from_datetime, '$lte': self.until_datetime}})
        self.data = list(cursor)

    def get(self, until_datetime):
        if len(self.data) > 0:
            if self.data[0]['date'] < until_datetime:
                d = self.data.pop(0)
                return d, d['date']
        return None, None

    def next(self):
        if len(self.data) > 0:
            d = self.data.pop(0)
            return d, d['date']        
        return None, None

    def is_realtime(self):
        return False

    def have_clock(self):
        return self.is_main_clock