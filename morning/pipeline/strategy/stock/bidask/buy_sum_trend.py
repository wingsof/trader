


class BidAskBuySumTrend:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, data):
        if self.next_elements is not None:
            self.next_elements.received(data)
