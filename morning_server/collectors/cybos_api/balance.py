import win32com.client

def get_balance(account_num, account_type):
    acc_obj = win32com.client.gencache.EnsureDispatch('CpTrade.CpTdNew5331A')
    acc_obj.SetInputValue(0, account_num)
    acc_obj.SetInputValue(1, account_type)
    acc_obj.BlockRequest()
    return acc_obj.GetHeaderValue(47)


if __name__ == '__main__':
    import trade_util
    tu = trade_util.TradeUtil()
    print(get_balance(tu.get_account_number(), tu.get_account_type()))

