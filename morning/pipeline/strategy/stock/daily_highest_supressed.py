from morning.logging import logger
from datetime import datetime, timedelta
import pandas as pd



class DailyHighestSuppressed:
    def __init__(self, search_days = 180):
        self.next_elements = None
        self.done = False
        self.entered = (False, None)
        self.search_days = search_days
        self.past_highest = 0
        self.df = None

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
        from morning.cybos_api import stock_chart
        l, day_datas = stock_chart.get_day_period_data(target, datetime.now() - timedelta(days=self.search_days), datetime.now())
        if l == 0:
            return False

        self.past_highest = [d['3'] for d in day_datas].max()
        return True

    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)
        
        if self.next_elements is not None and not self.done:
            if self.past_highest == 0:
                if not self.get_past_record(datas[-1]['target']):
                    logger.print(datas[-1]['target'], 'no daily records')
                    self.done = True
                
                if not self.entered[0]:
                    for d in datas:
                        if d['current_price'] > self.past_highest:
                            self.entered = (True, d['date'])
                    
                    if self.entered[0]:
                        self.df = pd.DataFrame(datas)
                else:
                    self.df.append(datas, ignore_index = True)
                    time_passed = d['date'] - self.entered[1]
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
        for name, group in self.df.groupby(pd.Grouper(freq='180s')):
            if len(group) > 0:
                minute_df = minute_df.append({'date':name, 'code': group['code'].iloc[0], 'open': group['price'].iloc[0],
                                            'low': group['price'].min(), 'high': group['price'].max(),
                                            'close': group['price'].iloc[-1], 'avg': group['price'].mean(), 'volume': group['volume'].sum()}, ignore_index = True)

        if minute_df(len) > 0:
            last = minute_df.iloc[-1]
            cutted = minute_df.iloc[1:-1, :]
            if len(cutted[cutted['avg'] < last['close']]) == 0:
                return True
        
        return False