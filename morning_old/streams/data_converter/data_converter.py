from abc import *

class DataConverter(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def vendor(self):
        return ''

    @abstractmethod 
    def accept_in(self):
        return ['']

    @abstractmethod
    def output_format(self):
        return ''
