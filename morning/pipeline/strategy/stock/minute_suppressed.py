

from morning.back_data.fetch_stock_data import get_day_past_highest


class MinuteSuppressed:
    def __init__(self):
        self.past_highest = 0

    def get_past_record(self, target):
        self.past_highest = get_day_past_highest(target, self.date, self.search_days)
        if self.past_highest == 0:
            return False

        return True

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