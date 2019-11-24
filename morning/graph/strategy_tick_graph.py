import pandas as pd
from datetime import datetime, time
import matplotlib.pyplot as plt
import mpl_finance


class StrategyTickGraph:
    def __init__(self):
        self.date = None
        self.codes = []
        self.df = pd.DataFrame(columns=['Date', 'Code', 'Price', 'Volume'])

    def tick_connect(self, strategy):
        strategy.add_graph(self)

    def filter_date(self, d):
        self.date = d

    def filter_codes(self, codes):
        self.codes.extend(codes)

    def out_min_graph(self):
        self.df.to_excel('test.xlsx')

        for c in self.codes:
            df = self.df[self.df['Code'] == c]
            df = df.set_index('Date')
            # 1. date key 가 있다는 전제로 할 건지...
            # 2. date filter?
            # 3. Group by로 할 경우, 있는 데이터 기반으로 하지, 빈 시간은 표현 안됨..
            if len(df) > 0:
                self.min_df = pd.DataFrame(columns = ['Date', 'Code', 'Open', 'Low', 'High', 'Close', 'Volume'])
                for name, group in df.groupby(pd.Grouper(freq='60s')):
                    self.min_df.append({'Date':name, 'Code': group['Code'].iloc[0], 'Open': group['Price'].iloc[0],
                                        'Low': group['Price'].min(), 'High': group['Price'].max(),
                                        'Close': group['Price'].iloc[-1], 'Volume': group['Volume'].sum()}, 
                                        ignore_index = True)
                fig = plt.figure(figsize=(12, 8))
                ax = fig.add_subplot(111)
                mpl_finance.candlestick2_ohlc(ax, self.min_df['Open'], self.min_df['High'], self.min_df['Low'], self.min_df['Close'], width = 0.5, colorup='r', colordown='b')
                plt.savefig(c + '.png')

    def received(self, datas):
        for d in datas:
            if len(self.codes) > 0 or d['code'] in self.codes:
                date = None
                if 'date' in d and self.date is not None:
                    db_date = d['date']
                    if db_date.date() != self.date:
                        continue
                
                if 'date' in d:
                    date = d['date']
                else:
                    date = datetime.now()
                    minsec = d['time_with_sec']
                    hour, minute, second = int(minsec / 10000), int(minsec % 10000 / 100), int(minsec % 100)
                    date.replace(hour = hour, minute = minute, second = second)
                print(d['time_with_sec'])
                row = {'Date': date, 'Code': d['code'], 'Price': d['current_price'], 'Volume': d['volume']}
                self.df = self.df.append(row, ignore_index = True)
        