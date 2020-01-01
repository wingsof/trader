from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.signal import find_peaks, peak_prominences
from utils import time_converter


def get_trend_value(x):
    if x is None:
        return 1
    elif not x:
        return 2
    
    return 3

class TrendFinder:
    # Up to yesterday data
    def __init__(self, code, d, min_data, write_graph = False):
        self.code = code
        self.today = d
        self.minute_data = min_data
        
        self.write_graph = write_graph
        if write_graph:
            self.shapes = []
        self.moving_average = np.array([])
        self.price_array = np.array([])
        self.date_array = np.array([])
        for data in min_data:
            dt = time_converter.intdate_to_datetime(data['0'])
            dt = dt.replace(hour=int(data['time'] / 100), minute=int(data['time'] % 100))
            data['date'] = dt
            self.price_array = np.append(self.price_array, [data['close_price']])
            self.date_array = np.append(self.date_array, [dt])
            if len(self.price_array) < 10:
                self.moving_average = np.append(self.moving_average, [self.price_array.mean()])
            else:
                self.moving_average = np.append(self.moving_average, [self.price_array[-10:].mean()])

    def _get_reversed(self, s):
        distance_from_mean = s.mean() - s
        return distance_from_mean + s.mean()

    def _find_trend(self, x, indexes, prominences, is_upper):
        if not is_upper and indexes.shape[0] < 2:
            return None, None
        elif is_upper and indexes.shape[0] < 2:
            return None, None
        
        short_trend = x[indexes[-1]] - x[indexes[-2]] > 0

        for i, v1 in enumerate(reversed(indexes)):
            for v2 in reversed(indexes[:indexes.shape[0] - 1 - i]):
                found = True
                for c in indexes:
                    if v1 == c or v2 == c: continue
                    x1, x2, y1, y2, cx, cy = v1, v2, x[v1], x[v2], c, x[c]
                    result = (y1 - y2) * cx + (x2 - x1) * cy + x1 * y2 - x2 * y1

                    if (is_upper and result < 0) or (not is_upper and result > 0):
                        found = False
                        break
                
                if found:
                    return short_trend, x[v1] - x[v2] > 0
        return short_trend, False

    def _calculate(self, x):
        peaks, _ = find_peaks(x, distance=10)
        prominences = peak_prominences(x, peaks)[0]

        peaks = np.extract(prominences > x.mean() * 0.002, peaks)
        prominences = np.extract(prominences > x.mean() * 0.002, prominences)
        return peaks, prominences


    def process_graph(self, peaks_top, peaks_bottom, bottom_short, bottom_long):
        df = pd.DataFrame(self.minute_data)
        for pt in peaks_top:
            close_price = self.moving_average[pt]
            dt = self.date_array[pt]
            self.shapes.append(dict(type='circle', x0=dt - timedelta(minutes=1), x1=dt + timedelta(minutes=1),
                                    y0=close_price-(close_price*0.01), y1=close_price+(close_price*0.01), xref='x', yref='y', line_color='orange'))

        for pb in peaks_bottom:
            close_price = self.moving_average[pb]
            dt = self.date_array[pb]
            self.shapes.append(dict(type='circle', x0=dt - timedelta(minutes=1), x1=dt + timedelta(minutes=1),
                                    y0=close_price-(close_price*0.01), y1=close_price+(close_price*0.01), xref='x', yref='y', line_color='LightSeaGreen'))

        fig = make_subplots(rows=3, cols=1)
        fig.add_trace(go.Candlestick(x=df['date'], open=df['start_price'],
                        high=df['highest_price'], close=df['close_price'],
                        low=df['lowest_price'],
                        increasing_line_color='red', decreasing_line_color='blue'), row=1, col=1)
        fig.add_trace(go.Scatter(x=self.date_array, y=self.moving_average, line=dict(color='green')), row=1, col=1)
        fig.add_trace(go.Bar(x=df['date'], y=df['volume']), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['cum_buy_volume'], name='cumulative buy', line=dict(color='red')), row=3, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['cum_sell_volume'], name='cumulative sell', line=dict(color='blue')), row=3, col=1)
        fig.update_layout(title=self.code, yaxis_tickformat='d', shapes=self.shapes)
        prefix = self.today.strftime('%Y%m%d_')
        fig.write_html(prefix + self.code + '_' + str(bottom_short) + '_' + str(bottom_long) + '.html', auto_open=False)

    def get_trend(self):
        timing_index = -1
        for i, d in enumerate(self.date_array):
            if d.hour >= 15 and d.minute < 20:
                timing_index = i
                break
        if timing_index == -1:
            return 0, 0, 0, 0

        reverse_prices = self._get_reversed(self.moving_average[:timing_index + 1])
        peaks_top, prominences_top = self._calculate(self.moving_average[:timing_index+1])
        peaks_bottom, prominences_bottom = self._calculate(reverse_prices)

        trend_top = self._find_trend(self.moving_average[:timing_index+1], peaks_top, prominences_top, True)
        trend_bottom = self._find_trend(self.moving_average[:timing_index+1], peaks_bottom, prominences_bottom, False)

        if self.write_graph:
            self.process_graph(peaks_top, peaks_bottom, get_trend_value(trend_bottom[0]), get_trend_value(trend_bottom[1]))
        return get_trend_value(trend_top[0]), get_trend_value(trend_top[1]), get_trend_value(trend_bottom[0]), get_trend_value(trend_bottom[1])
