import win32com.client
import sys

class TradeUtil:
    def __init__(self):
        self.trade_obj = win32com.client.Dispatch('CpTrade.CpTdUtil')
        if self.trade_obj.TradeInit(0) != 0:
            print('Trade Init Failed')
            sys.exit(1)

    def get_account_number(self):
        return self.trade_obj.AccountNumber[0]

    def get_account_type(self):
        return self.trade_obj.GoodsList(self.get_account_number(), 1)[0]


if __name__ == '__main__':
    tu = TradeUtil()
    print(tu.get_account_number())
    print(tu.get_account_type())

