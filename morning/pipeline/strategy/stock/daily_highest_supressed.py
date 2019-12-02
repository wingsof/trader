from morning.logging import logger
from datetime import datetime, timedelta
import pandas as pd
from utils import time_converter
from morning.config import db
from pymongo import MongoClient
from morning.back_data.fetch_stock_data import get_day_past_highest

class DailyHighestSuppressed:
    def __init__(self, date, search_days = 180):
        self.next_elements = None
        self.done = False
        self.date = date
        self.entered = (False, None)
        self.search_days = search_days
        self.past_highest = 0
        self.df = None
        self.graph_adder = []

    def add_graph(self, adder):
        self.graph_adder.append(adder)

    def finalize(self):
        for g in self.graph_adder:
            g.process()

        if self.next_elements:
            self.next_elements.finalize()

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def get_past_record(self, target):
        self.past_highest = get_day_past_highest(target, self.date, self.search_days)
        if self.past_highest == 0:
            return False

        return True

    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)
        
        if self.next_elements is not None and not self.done:
            if self.past_highest == 0:
                if not self.get_past_record(datas[-1]['target']):
                    logger.print(datas[-1]['target'], 'no daily records')
                    self.done = True
                    return
                
            if not self.entered[0]:
                for d in datas:
                    if d['current_price'] > self.past_highest:
                        self.entered = (True, d['date'])
                        logger.print('entered')
                        
                
                if self.entered[0]:
                    self.df = pd.DataFrame(datas)
                    self.df = self.df.set_index('date')
                    for g in self.graph_adder:
                            g.set_flag(datas[-1]['date'], 'ENTERED:' + str(self.past_highest))
            else:
                self.df.append(datas, ignore_index = True)
                time_passed = datas[-1]['date'] - self.entered[1]
                if time_passed > timedelta(minutes = 9):
                    if self.check_dataframe(self.df):
                        self.next_elements.received([{'name':self.__class__.__name__, 
                                                    'target': datas[-1]['target'],
                                                    'stream': datas[-1]['stream'],
                                                    'date': datas[-1]['date'],
                                                    'value': True, 
                                                    'price': datas[-1]['current_price']}])
                        for g in self.graph_adder:
                            g.set_flag(datas[-1]['date'], 'SUPRESSED')
                        self.done = True
        

    def check_dataframe(self, df):
        minute_df = pd.DataFrame(columns = ['date', 'code', 'open', 'low', 'high', 'close', 'avg', 'volume'])
        for name, group in df.groupby(pd.Grouper(freq='180s')):
            if len(group) > 0:
                minute_df = minute_df.append({'date':name, 'code': group['code'].iloc[0], 'open': group['current_price'].iloc[0],
                                            'low': group['current_price'].min(), 'high': group['current_price'].max(),
                                            'close': group['current_price'].iloc[-1], 'avg': group['current_price'].mean(), 'volume': group['volume'].sum()}, ignore_index = True)

        if len(minute_df) > 0:
            first = minute_df.iloc[0]
            last = minute_df.iloc[-1]
            cutted = minute_df.iloc[1:-1, :]
            
            if len(cutted) > 0 and len(cutted[cutted['avg'] < last['close']]) == 0 and first['close'] <= last['close']:
                return True
        
        return False