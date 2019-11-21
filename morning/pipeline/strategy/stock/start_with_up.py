from morning.logging import logger


class StartWithUp:
    def __init__(self, continuous):
        self.next_elements = None

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, data):
        logger.print(__file__)
        if self.next_elements is not None:
            self.next_elements.received(data)
