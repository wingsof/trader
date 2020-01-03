from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, peak_prominences
from utils import time_converter


def get_trend_value(x):
    if x is None:
        return 1
    elif not x:
        return 2
    
    return 3

class EdgeFinder:
    # Up to yesterday data
    def __init__(self, data):
        self.moving_average = np.array([])
        self.date_array = np.array([])
        for d in data:
            self.date_array = np.append(self.date_array, [d[0]])
            self.moving_average = np.append(self.moving_average, [d[1]])

    def _get_reversed(self, s):
        distance_from_mean = s.mean() - s
        return distance_from_mean + s.mean()

    def _calculate(self, x):
        peaks, _ = find_peaks(x, distance=10)
        prominences = peak_prominences(x, peaks)[0]

        peaks = np.extract(prominences > x.mean() * 0.002, peaks)
        prominences = np.extract(prominences > x.mean() * 0.002, prominences)
        return peaks, prominences

    def get_peaks(self, is_top, _with_prominence = False):
        peaks_data = []
        if not is_top:
            prices = self._get_reversed(self.moving_average)
        else:
            prices = self.moving_average
        peaks, prominence = self._calculate(prices)
        for p in peaks:
            peaks_data.append((self.date_array[p], self.moving_average[p]))

        if _with_prominence:
            return peaks, prominence
        return peaks_data

    def _get_short_trend(self, peaks):
        trend = []
        if len(peaks) >= 2:
            trend.append((self.date_array[peaks[-1]], self.moving_average[peaks[-1]],
                          self.date_array[peaks[-2]], self.moving_average[peaks[-2]]))
        return trend

    def _find_max_index(self, peaks):
        max_price = 0
        max_index = -1
        for p in peaks:
            if self.moving_average[p] > max_price:
                max_price = self.moving_average[p]
                max_index = p
        return max_index

    def _find_min_index(self, peaks):
        min_price = -1
        min_index = -1
        for p in peaks:
            if min_price == -1:
                min_price = self.moving_average[p]

            if self.moving_average[p] < min_price:
                min_price = self.moving_average[p]
                min_index = p
        return min_index

    def _get_right_indexes(self, peaks, start_index):
        right_peaks = []
        for p in peaks:
            if p > start_index:
                right_peaks.append(p)
        return right_peaks

    def _get_long_trend(self, peaks, is_top):
        start_index = -1
        if is_top:
            start_index = self._find_max_index(peaks)
        else:
            start_index = self._find_min_index(peaks)

        indexes = self._get_right_indexes(peaks, is_top)
        for p in indexes:
            found = True
            for i in peaks:
                if i != p and i != start_index:
                    x1, x2, y1, y2, cx, cy = start_index, p, self.moving_average[start_index], self.moving_average[p], i, self.moving_average[i]
                    result = (y1 - y2) * cx + (x2 - x1) * cy + x1 * y2 - x2 * y1
                    if (is_top and result < 0) or (not is_top and resut > 0):
                        found = False
                        break
            if found:
                return (self.date_array[start_index], self.moving_average[start_index],
                        self.date_array[p], self.moving_average[p]) 
        return None
            
    def find_trend(self):
        short_trends = []
        long_trends = []
        top_peaks, _ = self.get_peaks(True, True)
        bottom_peaks, _ = self.get_peaks(False, True)
        short_trends.extend(self._get_short_trend(top_peaks))
        short_trends.extend(self._get_short_trend(bottom_peaks))
        
        top_long = self._get_long_trend(top_peaks, True)
        bottom_long = self._get_long_trend(bottom_peaks, False) 

        if top_long is not None:
            long_trends.append(top_long)
        if bottom_long is not None:
            long_trends.append(bottom_long)

        return short_trends, long_trends
