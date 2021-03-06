from morning.logging import logger



class DeliverBidAsk:
    def __init__(self):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def finalize(self):
        if self.next_elements:
            self.next_elements.finalize()

    def received(self, datas):
        if self.next_elements is not None:
            keys = ['first_ask_price', 'second_ask_price',
                    'third_ask_price', 'fourth_ask_price',
                    'fifth_ask_price',
                    'first_bid_price', 'second_bid_price',
                    'third_bid_price', 'fourth_bid_price',
                    'fifth_bid_price']

            for d in datas:
                stream_name = d['stream']
                date = d['date']
                target = d['target']
                self.next_elements.received([{'name':self.__class__.__name__, 
                                            'target': target,
                                            'stream': stream_name, 
                                            'date': date,
                                            'value': [d[k] for k in keys]}])
