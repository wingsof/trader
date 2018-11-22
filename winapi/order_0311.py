import win32com.client

from winapi import balance_5331a as balance

class Order:
    ORDER_PRICE_RANGE = (1000000, 2000000)
    """
    LONG DICT TYPE
        [{'code': code, 'name': name, 'quantity': quantity,
         'sell_available': sell_available, 'price': price,
         'all_price': all_price}, ...]
    """
    def __init__(self, long_list, account_num, account_type):
        self.order_result_list = []
        self.long_list = long_list
        self.account_num = account_num
        self.account_type = account_type
        self.balance = balance.get_balance()
        """
        Use Dscbo1.CpConclusion
                elif self.name == "conclution" :
            # 주문 체결 실시간 업데이트
            conflag = self.client.GetHeaderValue(14)    # 체결 플래그
            ordernum = self.client.GetHeaderValue(5)    # 주문번호
            amount = self.client.GetHeaderValue(3)      # 체결 수량
            price = self.client.GetHeaderValue(4)       # 가격
            code = self.client.GetHeaderValue(9)        # 종목코드
            bs = self.client.GetHeaderValue(12)         # 매수/매도 구분
            balace = self.client.GetHeaderValue(23)  # 체결 후 잔고 수량
 
            conflags = ""
            if conflag in self.concdic :
                conflags = self.concdic.get(conflag)
                print(conflags)
 
            bss = ""
            if (bs in self.buyselldic):
                bss = self.buyselldic.get(bs)
 
            print(conflags, bss, code, "주문번호:", ordernum)
            # call back 함수 호출해서 orderMain 에서 후속 처리 하게 한다.
            self.parent.monitorOrderStatus(code, ordernum, conflags, price, amount, balace)
            return
        """

    def process(self, code, account_num, account_type, price, is_buy):
        if is_buy:
            quantity = self.get_available_buy_quantity(price)
        else:
            quantity = self.get_available_sell_quantity(code)

        if quantity is 0:
            print("Failed")
        else:
            self.obj = win32com.client.Dispatch('CpTrade.CpTd0311')
            order_type = '1' if is_buy else '2'
            self.obj.SetInputValue(0, order_type)
            self.obj.SetInputValue(1, account_num)
            self.obj.SetInputValue(2, account_type)
            self.obj.SetInputValue(3, code)
            self.obj.SetInputValue(4, quantity)
            self.obj.SetInputValue(5, price)
            self.obj.BlockRequest()

            if order_type == '1':
                self.balance -= quantity * price

            result = {
                'type_code': self.obj.GetHeaderValue(0),
                'account_num': self.obj.GetHeaderValue(1),
                'account_type': self.obj.GetHeaderValue(2),
                'code': self.obj.GetHeaderValue(3),
                'quantity': self.obj.GetHeaderValue(4),
                'price': self.obj.GetHeaderValue(5),
                'order_num': self.obj.GetHeaderValue(8),
                'account_name': self.obj.GetHeaderValue(9),
                'name': self.obj.GetHeaderValue(10)
                'order_type': self.obj.GetHeaderValue(12)
            }
            self.order_result_list.append(result)

    def get_available_buy_quantity(self, price):
        available_quantity = 0
        all_price = 0
        while True:
            all_price += price

            if all_price > Order.ORDER_PRICE_RANGE[1] or all_price > self.balance:
                break
            available_quantity += 1

        if available_quantity * price < Order.ORDER_PRICE_RANGE[0]:
            return 0

        return available_quantity

    def get_available_sell_quantity(self, code):
        for l in self.long_list:
            if l['code'] == code:
                return l['quantity']
        return 0

    def process_buy_order(self, buy_dict):
        # [expected, price]
        sorted_by_expected = sorted(buy_dict.items(), key=lambda kv: kv[1][0], reverse=True)
        for item in sorted_by_expected:
            if item[1][1] == 0:
                continue
            self.process(item[0], self.account_num, self.account_type, item[1][1], True)

    def process_sell_order(self, sell_dict):
        keys = list(sell_dict)
        for k in keys:
            if sell_dict[k][1] == 0:
                continue
            self.process(k, self.account_num, self.account_type, sell_dict[k][1], False)
