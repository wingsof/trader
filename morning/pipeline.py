



# TODO: define accept type for each elements and check when linking together
class Pipeline:
    testing = 0

    def __init__(self):
        self.first_element = None
        self.summary_data = None
        self.test_dummy = None

    def pipe_in(self, tick):
        if self.first_element is not None:
            self.first_element.stream_in_data(tick)

    def pipe_out(self, data):
        if Pipeline.testing:
            self.test_dummy = data
        # should have a result after processing data
        
    def result(self):
        if Pipeline.testing:
            return self.test_dummy
        # BUY / HOLD / SELL / NONE, BUY / SELL Prices (Array)
        return self.summary_data

    def set_elements(self, *args):
        if len(args) == 0:
            return False

        first_ele = args[0]
        last_ele = args[-1]

        self.first_element = first_ele
        if len(args) == 1:
            first_ele.set_output(self.pipe_out)
        else:
            for i, ele in enumerate(args):
                if i < len(args) - 1:
                    ele.set_output(args[i + 1].stream_in_data)
            last_ele.set_output(self.pipe_out)


if __name__ == '__main__':
    class DummyFilter:
        def __init__(self):
            self.next = None

        def set_output(self, next):
            self.next = next

        def stream_in_data(self, data):
            assert(data == [1,2,3])
            data.remove(1)
            self.next(data)

    class DummyStrategy:
        def __init__(self):
            self.next = None
            self.bought = False
        
        def set_output(self, next):
            set.next = next

        def stream_in_data(self, data):
            if data[0] < data[1]:
                if self.bought:
                    

    Pipeline.testing = 1
    pipeline = Pipeline()
    
    assert(pipeline.result() == None)

    pipeline = Pipeline()
    pipeline.set_elements(DummyFilter())
    pipeline.pipe_in([1,2,3])

    assert(pipeline.result() == [2,3])

