import win32com.client

class LongManifest:
    def __init__(self, account_num):
        self.account_num = account_num

    def get_count(self):
        self.stock_obj = win32com.client.Dispatch('CpTrade.CpTd6033')
        self.stock_obj.SetInputValue(0, self.account_num)
        self.stock_obj.SetInputValue(1, '1')
        self.stock_obj.SetInputValue(1, 50)
        self.stock_obj.BlockRequest()
        return self.stock_obj.GetHeaderValue(7)

    def get_long_list(self):
        self.stock_obj = win32com.client.Dispatch('CpTrade.CpTd6033')
        self.stock_obj.SetInputValue(0, self.account_num)
        self.stock_obj.SetInputValue(1, '1')
        self.stock_obj.SetInputValue(1, 50)
        self.stock_obj.BlockRequest()

        long_list = []
        for i in range(self.get_count()):
            code = self.stock_obj.GetDataValue(12, i)
            name = self.stock_obj.GetDataValue(0, i)
            quantity = self.stock_obj.GetDataValue(7, i)
            sell_available = self.stock_obj.GetDataValue(15, i)
            price = self.stock_obj.GetDataValue(17, i)
            all_price = price * quantity
            d = {'code': code, 'name': name, 'quantity': quantity,
                 'sell_available': sell_available, 'price': price,
                 'all_price': all_price}
            long_list.append(d)
        return long_list

    def get_long_codes(self):
        long_list = self.get_long_list()
        long_codes = []
        for i in long_list:
            long_codes.append(i['code'])
        return long_codes
