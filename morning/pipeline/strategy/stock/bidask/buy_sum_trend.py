from morning.logging import logger



class BidAskBuySumTrend:
    def __init__(self):
        self.next_elements = None
        self.sent = False

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            if not self.sent:
                self.next_elements.received([{'name':self.__class__.__name__, 'type': 'Bool', 'value': 'True'}])
                self.sent = True
