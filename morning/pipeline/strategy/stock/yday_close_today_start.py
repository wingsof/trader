



class YdayCloseTodayStart:
    def __init__(self, inverse):
        self.inverse = inverse
        self.next_elements = None
        self.yesterday_close = 0


    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.yesterday_close == 0:
            pass # set yesterday price
        else:
            pass 
            # if open price is higher than yesterday_close then 
            #   highest price - open price set as profit rate and deliver to next