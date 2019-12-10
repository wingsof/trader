from datetime import datetime, timedelta
import numpy as np
from scipy.signal import find_peaks, peak_prominences

from morning.back_data.fetch_stock_data import get_day_past_highest
from morning.logging import logger

class MinuteSuppressed:
    def __init__(self):
        self.graph_adder = []
        self.next_elements = None
        self.open_price = 0
        self.moving_average = np.array([])
        self.current_stage = 0
        self.buy_margin_price = [0, 0]
        self.buy_hold = None
        self.price_array = np.array([])
        self.done = False

    def add_graph(self, adder):
        self.graph_adder.append(adder)

    def finalize(self):
        for g in self.graph_adder:
            g.process()

        if self.next_elements:
            self.next_elements.finalize()

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def _get_reversed(self, s):
        distance_from_mean = s.mean() - s
        return distance_from_mean + s.mean()

    def _find_trend(self, x, indexes, prominences, is_upper):
        if not is_upper and indexes.shape[0] < 3:
            return False, False
        elif is_upper and indexes.shape[0] < 3:
            return False, True
        
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

        peaks = np.extract(prominences > x.mean() * 0.003, peaks)
        prominences = np.extract(prominences > x.mean() * 0.003, prominences)
        peaks = np.r_[np.array([0]), peaks]
        return peaks, prominences

    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)

        if self.done: return
        
        for d in datas:
            if d['date'].hour >= 15:
                if self.next_elements is not None and self.buy_hold is not None:
                    self.next_elements.received([{'name': self.__class__.__name__,
                                                    'target': d['target'],
                                                    'stream': d['stream'],
                                                    'date': d['date'],
                                                    'value': False, 'price': d['close_price']}])
                self.done = True
            elif self.buy_hold is not None and d['date'] - self.buy_hold < timedelta(minutes=10):
                continue

            if self.open_price == 0:
                self.open_price = d['start_price']

            self.price_array = np.append(self.price_array, [d['close_price']])
            if len(self.price_array) < 10:
                self.moving_average = np.append(self.moving_average, [self.price_array.mean()])
                continue
            else:
                self.moving_average = np.append(self.moving_average, [self.price_array[-10:].mean()])

            reverse_prices = self._get_reversed(self.moving_average)
            peaks_top, prominences_top = self._calculate(self.moving_average)
            peaks_bottom, prominences_bottom = self._calculate(reverse_prices)

            trend_top = self._find_trend(self.moving_average, peaks_top, prominences_top, True)
            trend_bottom = self._find_trend(self.moving_average, peaks_bottom, prominences_bottom, False)

            volume_trend = d['cum_buy_volume'] > d['cum_sell_volume']
            price_exceed = (d['close_price'] - self.open_price) / self.open_price * 100. > 15.
            bottom = trend_bottom[0] and trend_bottom[1]
            top = trend_top[0] and trend_top[1]
            

            if self.current_stage == 0:
                if bottom and not top and volume_trend and not price_exceed:
                    self.current_stage = 1
                    self.buy_margin_price[0] = self.moving_average[peaks_top[-1]]
                    self.buy_margin_price[1] = self.moving_average[peaks_top[-2]] if len(peaks_top) > 1 else self.moving_average[peaks_top[-1]]
            elif self.current_stage == 1:
                
                lowest_price, highest_price = 0, 0
                if not volume_trend or not bottom:
                    if self.buy_hold is not None:
                        self.buy_hold = None
                        if self.next_elements is not None:
                            self.next_elements.received([{'name': self.__class__.__name__,
                                                            'target': d['target'],
                                                            'stream': d['stream'],
                                                            'date': d['date'],
                                                            'value': False, 'price': d['close_price']}])
                    self.current_stage = 0
                else:
                    if len(self.moving_average) > 50:
                        lowest_price = self.moving_average[:-50].min()
                        highest_price = self.moving_average[:-50].max()
                    else:
                        lowest_price = self.moving_average.min()
                        highest_price = self.moving_average.max()
                    risk = float("{0:.2f}".format((highest_price - lowest_price) / lowest_price * 100.))
                    is_cross_margin = self.moving_average[-1] > self.buy_margin_price[0] or self.moving_average[-1] > self.buy_margin_price[1]
                    over_price = (d['close_price'] - self.open_price) / self.open_price * 100 > 10.
                    if self.buy_hold is None and is_cross_margin and risk < 13. and not over_price:
                        logger.print(d['date'], d['target'], 'BUY')
                        self.buy_hold = d['date']
                        if self.next_elements is not None:
                            self.next_elements.received([{'name': self.__class__.__name__,
                                                            'target': d['target'],
                                                            'stream': d['stream'],
                                                            'date': d['date'],
                                                            'value': True, 'price': d['close_price'], 'risk': risk}])
                        # Handle risk

                    



        