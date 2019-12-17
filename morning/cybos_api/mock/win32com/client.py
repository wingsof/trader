

class Dispatch:
    AccountNumber = [123456, 0]
    def __init__(self, obj_name):
        self.obj_name = obj_name

    def TradeInit(self, i):
        return 0

    def GoodsList(self, account_num, index):
        return ['49', '49']



