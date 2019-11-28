from pymongo import MongoClient
from morning.config import db
from morning.logging import logger
import pandas as pd


class DatabaseTick:
    def __init__(self, from_datetime, until_datetime, check_whole_data, is_main_clock = False):
        self.is_main_clock = is_main_clock
        self.from_datetime = from_datetime
        self.until_datetime = until_datetime
        self.check_whole_data = check_whole_data
        self.child_streams = []
        self.next_elements = None
        self.save_to_excel = False
        self.target_code = ''

    def is_acceptable_target(self, code):
        return code.startswith('cybos:A')

    def set_save_to_excel(self, is_save):
        self.save_to_excel = is_save

    def set_target(self, target):
        code = target.split(':')[1]
        self.target_code = code
        stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
        
        cursor = stock[code].find({'date': {'$gte':self.from_datetime, '$lte': self.until_datetime}})
        self.data = list(cursor)
        logger.print(target, 'Length', len(self.data))
        if len(self.data) > 0 and self.check_whole_data:
            df = pd.DataFrame(self.data)

            if self.save_to_excel:
                df.to_excel(code + '_from_db.xlsx')

            market = df['20']
            if len(market[market == 49]) > 10 and len(market[market == 50]) > 100 and len(market[market == 53]) > 10:
                pass
            else:
                self.data = []
                logger.print('Abnormal detected', target)

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

    def add_child_streams(self, s):
        self.child_streams.append(s)

    def finalize(self):
        for c in self.child_streams:
            c.finalize()
        
        if self.next_elements:
            self.next_elements.finalize()

    def received(self, data):
        if len(self.data) > 0:
            d = self.data.pop(0)
            for c in self.child_streams:
                c.clock(d['date'])

            d['stream'] = self.__class__.__name__
            d['target'] = self.target_code
            if self.next_elements:
                self.next_elements.received([d])

        return len(self.data)

    def is_realtime(self):
        return False

    def have_clock(self):
        return self.is_main_clock
