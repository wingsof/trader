from PyQt5.QtCore import QAbstractTableModel


class BidAskModel(QAbstractTableModel):
    def __init__(self):
        super(BidAskModel, self).__init__()

    def rowCount(self, parent):
        return 3

    def columnCount(self, parent):
        return 5

    def data(self, index, role):
        if not index.isValid():
            return None