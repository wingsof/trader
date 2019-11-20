from PyQt5.QtCore import QObject, pyqtSignal

class Chooser(QObject):

    selection_changed = pyqtSignal(set)

    def __init__(self):
        super().__init__()

    def start(self):
        pass


