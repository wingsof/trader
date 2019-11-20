from pymongo import MongoClient
from morning.config import db


class DatabaseTick:
    def __init__(self, from_datetime, until_datetime, is_main_clock = False):
        self.is_main_clock = is_main_clock
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime
        self.child_streams = []
        self.next_elements = None

    def set_target(self, code):
        db = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        
        cursor = db[code].find({'date': {'$gte':self.from_datetime, '$lte': self.until_datetime}})
        self.data = list(cursor)

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def clock(self, until_datetime):
        datas = []
        while len(self.data) > 0:
            if self.data[0]['date'] < until_datetime:
                datas.append(self.data.pop(0))
            else:
                break
        if self.next_elements:
            self.next_elements.received(datas)

    def add_chlid_streams(self, s):
        self.child_streams.append(s)

    def next(self):
        if len(self.data) > 0:
            d = self.data.pop(0)
            for c in child_streams:
                c.clock(d['date'])

            if self.next_elements:
                self.next_elements.received([c])       
        return len(self.data)

    def is_realtime(self):
        return False

    def have_clock(self):
        return self.is_main_clock