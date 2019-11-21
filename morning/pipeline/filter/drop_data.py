from morning.logging import logger


class DropDataFilter:
    def __init__(self, drop_count):
        self.next_elements = None
        self.drop_count = drop_count

    def set_output(self, next_ele):
        self.next_elements = next_ele

    def received(self, datas):
        if self.next_elements is not None:
            if self.drop_count > 0:
                self.drop_count -= 1
                logger.print('DropDataFilter', datas)
            else:
                self.next_elements.received(datas)