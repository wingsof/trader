from pymongo import MongoClient
from morning.config import db


class DatabaseBidAskTick:
    def __init__(self, from_datetime, until_datetime, check_whole_data, is_main_clock = False):
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime
        self.check_whole_data = check_whole_data
        self.is_main_clock = is_main_clock
        self.target_code = ''

    def is_acceptable_target(self, code):
        return code.startswith('cybos:A')

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def set_target(self, target):
        code = target.split(':')[1]
        self.target_code = code
        stock_ba = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        
        cursor = stock_ba[code + '_BA'].find({'date': {'$gte':self.from_datetime, '$lte': self.until_datetime}})
        self.data = list(cursor)

    def clock(self, until_datetime):
        datas = []
        while len(self.data) > 0:
            if self.data[0]['date'] < until_datetime:
                d = self.data.pop(0)
                d['stream'] = self.__class__.__name__
                d['target'] = self.target_code
                datas.append(d)
            else:
                break
        if self.next_elements:
            self.next_elements.received(datas)

    def received(self, data):
        if len(self.data) > 0:
            d = self.data.pop(0)
            #TODO: nothing to do alone, how to handle it?

    def is_realtime(self):
        return False

    def have_clock(self):
        return self.is_main_clock
