from morning.logging import logger


class DropDataFilter:
    def __init__(self, drop_count):
        self.next_elements = []
        self.drop_count = drop_count

    def set_output(self, next_ele):
        self.next_elements.append(next_ele)

    def received(self, datas):
        if len(self.next_elements) > 0:
            if self.drop_count > 0:
                self.drop_count -= 1
                logger.print('DropDataFilter', datas)
            else:
                for n in self.next_elements:
                    n.received(datas)
