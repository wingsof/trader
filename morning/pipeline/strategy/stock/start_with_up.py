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

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
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
                    if self.check_dataframe():
                        pass # Deliver passed result
                    self.done = True
                else:
                    self.df = pd.concat([self.df, pd.DataFrame(datas)])

            #self.next_elements.received(datas)
    def check_dataframe(self):
        start_time = self.df['time_with_sec'][0]
        condition_met = True
        for i in range(self.cont_min):
            until_time = self._add_next_min(start_time)
            filtered_df = df[(df.time_with_sec >= start_time) & (df.time_with_sec < until_time)]
            if filtered_df['current_price'][-1] <= filtered_df['current_price'][0]:
                condition_met = False
                break
            until_time = start_time
        return condition_met

    def _add_next_min(self, t):
        h, m, s = int(t / 10000), int(t % 10000 / 100), int(t % 100)
        if m == 59:
            h += 1
            m = 0
        else:
            m += 1
        return h * 10000 + m * 100 + s
