import pandas as pd
from datetime import datetime, time, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TickMinGraphNeedle:
    def __init__(self, out_when_flag = False, write_to_html = False):
        self.date = None
        self.write_to_html = write_to_html
        self.codes = []
        self.data = []
        self.shapes = []
        self.annotations = []
        self.out_when_flag = out_when_flag
        self.figure = None
        self.extra_shapes_date = set()
        self.ma_array = None

    def tick_connect(self, strategy):
        strategy.add_graph(self)

    def filter_date(self, d):
        self.date = d

    def set_moving_average(self, dates, avgs):
        self.ma_array = (dates, avgs)
        
    def filter_codes(self, codes):
        self.codes.extend(codes)

    def set_circle_flag(self, date, value, is_up, desc= ''):
        if date not in self.extra_shapes_date:
            self.extra_shapes_date.add(date)
            print('set_circle_flag', date, value, is_up)
            color = "LightSeaGreen" if not is_up else "orange"
            self.shapes.append(
                dict(type='circle', x0=date-timedelta(minutes=1), x1=date+timedelta(minutes=1), y0=value-(value*0.01), y1=value+(value*0.01), xref='x', yref='y', line_color=color))        
        
    def set_flag(self, date, desc):
        self.shapes.append(
            dict(x0=date, x1=date, y0=0, y1=1, xref='x', yref='paper', line_width=2))
        self.annotations.append(
            dict(x=date, y=0.05, xref='x', yref='paper', showarrow=True, xanchor='left', text=desc))


    def process(self):
        print('process')
        if self.out_when_flag and len(self.shapes) == 0:
            return

        if len(self.data) > 0:
            prefix = ''
            code = self.data[0]['code']
            if self.date is not None:
                prefix = self.date.strftime('%Y%m%d_')
            else:
                prefix = (self.data[0]['date']).strftime('%Y%m%d_')
            df = pd.DataFrame(self.data)
            df = df.set_index('date')

            minute_df = pd.DataFrame(columns = ['date', 'code', 'open', 'low', 'high', 'close', 'volume', 'cum_buy', 'cum_sell', 'vol_speed'])
            for name, group in df.groupby(pd.Grouper(freq='180s')):
                if len(group) > 0:
                    buy_volume = group['cum_buy'].iloc[-1] - group['cum_buy'].iloc[0]
                    sell_volume = group['cum_sell'].iloc[-1] - group['cum_sell'].iloc[0]
                    minute_df = minute_df.append({'date':name, 'code': group['code'].iloc[0], 'open': group['open'].iloc[0],
                                                'low': group['low'].min(), 'high': group['high'].max(),
                                                'close': group['close'].iloc[-1], 'volume': group['volume'].sum(),
                                                'cum_buy': group['cum_buy'].iloc[-1], 'cum_sell': group['cum_sell'].iloc[-1],
                                                'buy_moment': buy_volume, 'sell_moment': sell_volume}, ignore_index = True)

            if len(minute_df) > 0:
                fig = make_subplots(rows=3, cols=1)
                fig.add_trace(go.Candlestick(x=minute_df['date'],
                                open=minute_df['open'], high=minute_df['high'],
                                low=minute_df['low'], close=minute_df['close'],
                                increasing_line_color='red', decreasing_line_color='blue'), row=1, col=1)
                if self.ma_array is not None:
                    fig.add_trace(go.Scatter(x=self.ma_array[0], y=self.ma_array[1], name='MA 20', line=dict(color='green')), row=1, col=1)
                fig.add_trace(go.Bar(x=minute_df['date'], y=minute_df['volume']), row=2, col=1)
                fig.add_trace(go.Scatter(x=minute_df['date'], y=minute_df['cum_buy'], name='culmulate buy', line=dict(color='red')), row=3, col=1)
                fig.add_trace(go.Scatter(x=minute_df['date'], y=minute_df['cum_sell'], name='culmulate sell', line=dict(color='blue')), row=3, col=1)
                #fig.add_trace(go.Scatter(x=minute_df['date'], y=minute_df['buy_moment'], name='buy moment', line=dict(color='red')), row=4, col=1)
                #fig.add_trace(go.Scatter(x=minute_df['date'], y=minute_df['sell_moment'], name='sell moment', line=dict(color='blue')), row=4, col=1)
                fig.update_layout(title=code, yaxis_tickformat='d', shapes=self.shapes, annotations=self.annotations, autosize=False, width=1200, height=1200,)
                if self.write_to_html:
                    fig.write_html(prefix+code+'.html', auto_open=False)
                else:
                    self.figure = fig

    def received(self, datas):
        db_date = datas[0]['date']
        code = datas[0]['target']
        if self.date is not None:
            if db_date.date() != self.date:
                return
        elif len(self.codes) > 0:
            if code not in self.codes:
                return

        for d in datas:                
            row = {'date': d['date'], 'code': d['target'], 
                    'open': d['start_price'], 'low': d['lowest_price'], 'high': d['highest_price'],
                    'close': d['close_price'], 'volume': d['volume'], 'cum_buy': d['cum_buy_volume'], 
                    'cum_sell': d['cum_sell_volume']}
            self.data.append(row)
        
        
