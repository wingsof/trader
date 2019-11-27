



class YdayCloseTodayStart:
    def __init__(self, inverse):
        self.inverse = inverse
        self.next_elements = None
        self.yesterday_close = 0

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            for d in datas:
                if self.yesterday_close > 0:
                    if self.compare_price(self.yesterday_close, d['start_price']):
                        profit_r = (d['highest_price'] - d['start_price']) / d['start_price'] * 100.
                        self.next_elements.received([{'name':self.__class__.__name__, 
                                                    'target': d['target'],
                                                    'stream': d['stream'], 
                                                    'date': d['date'],
                                                    'value': True, 'profit': profit_r}])

                self.yesterday_close = d['close_price']

    def compare_price(self, yday, current):
        if not self.inverse:
            if current > yday:
                return True
        else:
            if current < yday:
                return True
        return False