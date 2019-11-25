import pandas as pd


class TickExcelNeedle:
    def __init__(self):
        self.date = None
        self.codes = []
        self.df = None

    def tick_connect(self, strategy):
        strategy.add_graph(self)

    def filter_date(self, d):
        self.date = d

    def filter_codes(self, codes):
        self.codes.extend(codes)

    def process(self):
        if self.df is not None and len(self.df) > 0:
            prefix = self.date.strftime('%Y%m%d_')
            # groupby code and save to file
            for name, group in self.df.groupby('code'):
                if len(group) > 0:
                    suffix = group['code'].iloc[0] + '.xlsx'
                    group.to_excel(prefix + suffix)



    def received(self, datas):
        if len(datas) <= 0 or len(self.codes) == 0 or self.date is None:
            return

        db_date = datas[0]['date']
        if datas[0]['code'] in self.codes and db_date.date() == self.date:
            if self.df is None:
                self.df = pd.DataFrame(datas)
            else:
                self.df = self.df.append(datas, ignore_index = True)
