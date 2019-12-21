from datetime import datetime, timedelta
import numpy as np
from scipy.signal import find_peaks, peak_prominences

from morning.back_data.fetch_stock_data import get_day_past_highest
from morning.config import stock_time
from morning.logging import logger

class MinuteSuppressed:
    def __init__(self):
        self.graph_adder = []
        self.next_element = None
        self.open_price = 0
        self.moving_average = np.array([])
        self.current_stage = 0
        self.highest_after_buy = 0
        self.buy_margin_price = [0, 0]
        self.buy_hold = None
        self.price_array = np.array([])
        self.done = False
        self.date_array = np.array([])
        self.latest_tick = None

    def add_graph(self, adder):
        self.graph_adder.append(adder)

    def finalize(self):
        if self.buy_hold is not None:
            self._send_short()
            
        for g in self.graph_adder:
            g.set_moving_average(self.date_array, self.moving_average)
            g.process()

        if self.next_element:
            self.next_element.finalize()

    def set_output(self, next_ele):
        self.next_element = next_ele

    def _get_reversed(self, s):
        distance_from_mean = s.mean() - s
        return distance_from_mean + s.mean()

    def _find_trend(self, x, indexes, prominences, is_upper):
        if not is_upper and indexes.shape[0] < 2:
            return False, False
        elif is_upper and indexes.shape[0] < 2:
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
        return peaks, prominences

    def _send_short(self):
        self.buy_hold = None        
        if self.next_element is not None:
            self.next_element.received([{'name': self.__class__.__name__,
                                            'target': self.latest_tick['target'],
                                            'stream': self.latest_tick['stream'],
                                            'date': self.latest_tick['date'],
                                            'value': False,
                                            'price': self.latest_tick['close_price'],
                                            'highest': self.highest_after_buy}])
            

    def _handle_data(self, datas):
        if self.done: return

        for d in datas:
            self.latest_tick = d
            if (d['date'].hour >= stock_time.MARKET_CLOSE_HOUR  and 
                    d['date'].minute >= stock_time.STOCK_COVERING_MINUTE and self.buy_hold is not None):
                self._send_short()
                for g in self.graph_adder:
                        g.set_flag(d['date'], 'SELL')
                self.done = True
                break
            elif (d['date'].hour >= stock_time.STOCK_COVERING_MINUTE and 
                    d['date'].minute >= stock_time.STOCK_BUY_BLOCK_MINUTE and self.buy_hold is None):
                self.done = True
                break

            if self.open_price == 0:
                self.open_price = d['start_price']

            self.price_array = np.append(self.price_array, [d['close_price']])
            self.date_array = np.append(self.date_array, [d['date']])

            if len(self.price_array) < 10:
                self.moving_average = np.append(self.moving_average, [self.price_array.mean()])
                continue
            else:
                self.moving_average = np.append(self.moving_average, [self.price_array[-10:].mean()])


            if (self.buy_hold is not None and 
                    d['date'] - self.buy_hold < timedelta(minutes=stock_time.BUY_HOLD_DURATION_MINUTE)):
                continue
            #elif 'VI' in d and d['VI']:
            #    continue

            reverse_prices = self._get_reversed(self.moving_average)
            peaks_top, prominences_top = self._calculate(self.moving_average)
            peaks_bottom, prominences_bottom = self._calculate(reverse_prices)

            trend_top = self._find_trend(self.moving_average, peaks_top, prominences_top, True)
            trend_bottom = self._find_trend(self.moving_average, peaks_bottom, prominences_bottom, False)

            cum_sum = (d['cum_buy_volume'] + d['cum_sell_volume']) * 0.1
            volume_trend = d['cum_buy_volume'] > d['cum_sell_volume'] + cum_sum
            price_exceed = (d['close_price'] - self.open_price) / self.open_price * 100. > 15.
            bottom = trend_bottom[0] and trend_bottom[1]
            top = trend_top[0] and trend_top[1]
            
            for g in self.graph_adder:
                for p_top in peaks_top:
                    g.set_circle_flag(self.date_array[p_top], self.moving_average[p_top], True)
                for p_bottom in peaks_bottom:
                    g.set_circle_flag(self.date_array[p_bottom], self.moving_average[p_bottom], False)

            if self.current_stage == 0:
                if bottom and not top and volume_trend and not price_exceed:
                    self.current_stage = 1
                    if len(peaks_top) == 0:
                        continue
                    self.buy_margin_price[0] = self.moving_average[peaks_top[-1]]
                    self.buy_margin_price[1] = self.moving_average[peaks_top[-2]] if len(peaks_top) > 1 else self.moving_average[peaks_top[-1]]
            elif self.current_stage == 1:
                lowest_price, highest_price = 0, 0
                if volume_trend and bottom:
                    if len(self.moving_average) > 50:
                        lowest_price = self.moving_average[:-50].min()
                        highest_price = self.moving_average[:-50].max()
                    else:
                        lowest_price = self.moving_average.min()
                        highest_price = self.moving_average.max()
                    risk = float("{0:.2f}".format((highest_price - lowest_price) / lowest_price * 100.))
                    is_cross_margin = self.moving_average[-1] > self.buy_margin_price[0] or self.moving_average[-1] > self.buy_margin_price[1]
                    over_price = (d['close_price'] - self.open_price) / self.open_price * 100 > 10. # TODO : double check with price_exceed?
                    if self.buy_hold is None and is_cross_margin and risk < 13. and not over_price:
                        logger.print(d['date'], d['target'], 'BUY')
                        self.buy_hold = d['date']
                        if self.next_element is not None:
                            self.next_element.received([{'name': self.__class__.__name__,
                                                            'target': d['target'],
                                                            'stream': d['stream'],
                                                            'date': d['date'],
                                                            'value': True, 'price': d['close_price'], 
                                                            'risk': risk}])
                            self.current_stage = 2
                            self.highest_after_buy = d['close_price']
                        for g in self.graph_adder:
                            g.set_flag(d['date'], 'BUY')
                else:
                    self.current_stage = 0
            elif self.current_stage == 2:
                if d['highest_price'] > self.highest_after_buy:
                    self.highest_after_buy = d['highest_price']

                if (not volume_trend or not bottom) and self.buy_hold is not None:
                    
                    for g in self.graph_adder:
                        g.set_flag(d['date'], 'SELL')
                    self.current_stage = 0

                    
    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)

        self._handle_data(datas)
