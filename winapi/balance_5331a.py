import win32com.client

def get_balance(account_num, account_type):
    acc_obj = win32com.client.Dispatch('CpTrade.CpTdNew5331A')
    acc_obj.SetInputValue(0, account_num)
    acc_obj.SetInputValue(1, account_type)
    acc_obj.BlockRequest()
    return acc_obj.GetHeaderValue(45)

