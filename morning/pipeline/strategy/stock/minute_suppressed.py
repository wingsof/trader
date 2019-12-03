from datetime import datetime

from morning.back_data.fetch_stock_data import get_day_past_highest
from scipy.signal import argrelextrema
import numpy as np

class MinuteSuppressed:
    def __init__(self):
        self.past_highest = 0
        self.graph_adder = []
        self.date = None
        self.next_elements = None
        self.price_array = []

    def get_past_record(self, target):
        self.past_highest = get_day_past_highest(target, self.date, 12)
        if self.past_highest == 0:
            return False

        return True

    def add_graph(self, adder):
        self.graph_adder.append(adder)

    def finalize(self):
        array = np.array(self.price_array)
        local_minima = argrelextrema(array[:, [1]], np.less)
        print(type(local_minima))
        for m in local_minima[0]:
            print(m)
            for g in self.graph_adder:
                g.set_flag(array[m,0], '')
            
        for g in self.graph_adder:
            g.process()

        if self.next_elements:
            self.next_elements.finalize()

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)

        for d in datas:
            avg = (d['start_price'] + d['highest_price'] + d['close_price'] + d['lowest_price']) / 4
            self.price_array.append((d['date'],avg))



        