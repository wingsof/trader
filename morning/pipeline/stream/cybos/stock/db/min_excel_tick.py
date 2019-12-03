import pandas as pd


class MinExcelTick:
    def __init__(self, filename):
        self.next_elements = None
        self.df = pd.read_excel(filename)
        self.current_pos = 0

    def finalize(self):
        if self.next_elements:
            self.next_elements.finalize()

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, _):
        if self.current_pos < len(self.df):
            if self.next_elements:
                self.next_elements.received([self.df.iloc[self.current_pos].to_dict()])
            self.current_pos += 1

        return len(self.df) - self.current_pos