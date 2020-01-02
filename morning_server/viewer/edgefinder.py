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

    def get_peaks(self, is_top):
        peaks_data = []
        if not is_top:
            prices = self._get_reversed(self.moving_average)
        else:
            prices = self.moving_average
        peaks, _ = self._calculate(prices)
        for p in peaks:
            peaks_data.append((self.date_array[p], self.moving_average[p]))
        return peaks_data
        
    def get_trend(self):
        reverse_prices = self._get_reversed(self.moving_average)
        peaks_top, prominences_top = self._calculate(self.moving_average)
        peaks_bottom, prominences_bottom = self._calculate(reverse_prices)

        trend_top = self._find_trend(self.moving_average, peaks_top, prominences_top, True)
        trend_bottom = self._find_trend(self.moving_average, peaks_bottom, prominences_bottom, False)

        return peaks_top, peaks_bottom, trend_top, trend_bottom
