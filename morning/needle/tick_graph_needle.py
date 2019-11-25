import pandas as pd
from datetime import datetime, time
import matplotlib.pyplot as plt
import mpl_finance
import matplotlib.dates as matdates


class TickGraphNeedle:
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
        published = []
        for c in self.codes:
            df = self.df[self.df['Code'] == c]
            df = df.set_index('Date')
            # 2. date filter? : received 에서 date 확인했기 때문에 필요 없어 보임
            # 3. Group by로 할 경우, 빈 데이터는 group size 0으로 확인 가능
            if len(df) > 0:
                minute_df = pd.DataFrame(columns = ['Date', 'Code', 'Open', 'Low', 'High', 'Close', 'Volume'])
                for name, group in df.groupby(pd.Grouper(freq='60s')):
                    if len(group) > 0:
                        minute_df = minute_df.append({'Date':name, 'Code': group['Code'].iloc[0], 'Open': group['Price'].iloc[0],
                                            'Low': group['Price'].min(), 'High': group['Price'].max(),
                                            'Close': group['Price'].iloc[-1], 'Volume': group['Volume'].sum()}, 
                                            ignore_index = True)
                    else:
                        minute_df = minute_df.append({'Date':name, 'Code': c, 'Open': 0,
                                            'Low': 0, 'High': 0,
                                            'Close': 0, 'Volume': 0}, 
                                            ignore_index = True)
                if len(minute_df) > 0:
                    fig = plt.figure(figsize=(12, 8))
                    ax = fig.add_subplot(111)
                    
                    ohlc = minute_df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
                    ohlc['Date'] = ohlc['Date'].apply(matdates.date2num)
                    ohlc = ohlc.astype(float)
                    # for 5 data, .0005 is appropriate
                    mpl_finance.candlestick_ohlc(ax, ohlc.values, width=.0005, colorup='r', colordown='b')
                    ax.xaxis.set_major_formatter(matdates.DateFormatter('%H:%M'))
                    plt.xticks(rotation='vertical')
                    plt.savefig(c + '.png')
                    published.append(c)
                    
        return published


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
                
                row = {'Date': date, 'Code': d['code'], 'Price': d['current_price'], 'Volume': d['volume']}
                self.df = self.df.append(row, ignore_index = True)
        