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

    def set_flag(self, date, desc):
        pass

    def process(self):
        if self.df is not None and len(self.df) > 0:
            prefix = ''
            code = self.df['target'].iloc[-1]
            if self.date is not None:
                prefix = self.date.strftime('%Y%m%d_')
            else:
                prefix = self.df['date'].iloc[-1].strftime('%Y%m%d_')
            # groupby code and save to file
            self.df.to_excel(prefix + code + '.xlsx')

    def received(self, datas):
        db_date = datas[0]['date']
        code = datas[0]['target']
        if self.date is not None:
            if db_date.date() != self.date:
                return
        elif len(self.codes) > 0:
            if code not in self.codes:
                return
        if self.df is None:
            self.df = pd.DataFrame(datas)
        else:
            self.df = self.df.append(datas, ignore_index = True)

