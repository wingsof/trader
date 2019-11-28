from morning.logging import logger
from datetime import datetime, timedelta
import pandas as pd

class StartWithUp:
    def __init__(self, cont_min):
        self.next_elements = None
        self.cont_min = cont_min
        self.start_minsec = None
        self.done = False
        self.df = None
        self.graph_adder = []

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

        if self.next_elements is not None and not self.done:
            minsec = datas[0]['time_with_sec']
            hour, minute, second = int(minsec / 10000), int(minsec % 10000 / 100), int(minsec % 100)
            if self.start_minsec is None:
                self.start_minsec = datetime.now()
                self.start_minsec = self.start_minsec.replace(hour = hour, minute = minute, second = second)
                self.df = pd.DataFrame(datas)
            else:
                n = datetime.now()
                n = n.replace(hour = hour, minute = minute, second = second)
                if n - self.start_minsec > timedelta(minutes=self.cont_min):
                    if self.check_dataframe(self.df):
                        #logger.print({'name':self.__class__.__name__, 'type': 'Bool', 'value': 'True'}, minsec)
                        self.next_elements.received([{'name':self.__class__.__name__, 
                                                    'target': datas[-1]['target'],
                                                    'stream': datas[-1]['stream'],
                                                    'date': datas[-1]['date'],
                                                    'value': True, 
                                                    'price': datas[-1]['current_price']}])
                        for g in self.graph_adder:
                            g.set_flag(datas[-1]['date'], 'SUCCESS')
                    else:
                        logger.print(self.__class__.__name__, minsec, 'Fail')
                        for g in self.graph_adder:
                            g.set_flag(datas[-1]['date'], 'FAIL')
                    self.done = True
                else:
                    self.df = pd.concat([self.df, pd.DataFrame(datas)])

    def check_dataframe(self, df):
        start_time = df['time_with_sec'].iloc[0]
        condition_met = True
        for _ in range(self.cont_min):
            until_time = self._add_next_min(start_time)
            filtered_df = df[(df.time_with_sec >= start_time) & (df.time_with_sec < until_time)]

            if len(filtered_df) == 0 or filtered_df['current_price'].iloc[-1] <= filtered_df['current_price'].iloc[0]:
                condition_met = False
                break
            start_time = until_time

        return condition_met

    def _add_next_min(self, t):
        h, m, s = int(t / 10000), int(t % 10000 / 100), int(t % 100)
        if m == 59:
            h += 1
            m = 0
        else:
            m += 1
        return h * 10000 + m * 100 + s
