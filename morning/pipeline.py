


class Pipeline:
    def __init__(self):
        self.first_element = None

    def stream_in_data(self, tick):
        if self.first_element is not None:
            self.first_element.stream_in_data(tick)

    def summary_result(self, data):
        pass

    def set_elements(self, *args):
        if len(args) == 0:
            return False

        first_ele = args[0]
        last_ele = args[-1]
        mid_ele = args[1:-1]

        self.first_element = first_ele
        if len(args) == 1:
            first_ele.set_output(self.summary_result)
        else:
            for i, ele in enumerate(args):
                if i < len(args) - 1:
                    ele.set_output(args[i + 1].stream_in_data)
            last_ele.set_output(self.summary_result)
