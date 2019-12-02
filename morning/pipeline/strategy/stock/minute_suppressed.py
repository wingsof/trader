from datetime import datetime

from morning.back_data.fetch_stock_data import get_day_past_highest


class MinuteSuppressed:
    def __init__(self):
        self.past_highest = 0
        self.graph_adder = []
        self.date = None
        self.next_elements = None

    def get_past_record(self, target):
        self.past_highest = get_day_past_highest(target, self.date, 12)
        if self.past_highest == 0:
            return False

        return True

    def add_graph(self, adder):
        self.graph_adder.append(adder)

    def finalize(self):
        for g in self.graph_adder:
            g.process()

        if self.next_elements:
            self.next_elements.finalize()

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        for g in self.graph_adder:
            g.received(datas)

        if datas[0]['date'].hour == 14 and datas[0]['date'].minute == 20:
            g.set_flag(datas[-1]['date'], 'SUPRESSED')