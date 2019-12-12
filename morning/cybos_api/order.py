import win32com.client
import time
from morning.cybos_api import connection
from morning.logging import logger

class _OrderRealtime:
    def set_params(self, obj, order_obj):
        self.obj = obj
        self.order_obj = order_obj

    def OnReceived(self):
        flag = self.obj.GetHeaderValue(14)    # string flag '1': 체결, '2': 확인, '3': 거부, '4':접수
        # 매수, 매도는 (1)접수 -> (2)체결
        # 취소, 정정은 (1)접수 -> (2) 확인
        # 오류시에는 거부
        order_num = self.obj.GetHeaderValue(5)    # long order number 
        quantity = self.obj.GetHeaderValue(3)      # long quantity
        price = self.obj.GetHeaderValue(4)       # long price 
        code = self.obj.GetHeaderValue(9)        # code
        order_type = self.obj.GetHeaderValue(12) # string '1' 매도, '2' 매수
        total_quantity = self.obj.GetHeaderValue(23)    # count of stock left
        result = {
            'flag': flag,
            'code': code,
            'order_num': order_num,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'total_quantity': total_quantity
        }
        self.order_obj.order_event(result.copy())


class Order:
    def __init__(self, account_num, account_type, listener):
        self.conn = connection.Connection()
        self.listener = listener
        self.realtime_order = win32com.client.Dispatch('DsCbo1.CpConclusion')
        handler = win32com.client.WithEvents(self.realtime_order, _OrderRealtime)
        handler.set_params(self.realtime_order, listener)
        self.realtime_order.Subscribe()
  
    def stop(self):
        self.realtime_order.Unsubscribe()

    def process(self, code, quantity, account_num, account_type, price, is_buy):
        while self.conn.order_left_count() <= 0:
            logger.print("WAIT ORDER LEFT", code, quantity, is_buy, price)
            time.sleep(1)

        if quantity == 0:
            logger.print("Failed", code, quantity, is_buy, price)
        else:
            self.obj = win32com.client.Dispatch('CpTrade.CpTd0311')
            order_type = '2' if is_buy else '1'
            self.obj.SetInputValue(0, order_type)
            self.obj.SetInputValue(1, account_num)
            self.obj.SetInputValue(2, account_type)
            self.obj.SetInputValue(3, code)
            self.obj.SetInputValue(4, quantity)
            self.obj.SetInputValue(5, price)

            self.obj.BlockRequest()
            return self.obj.GetDibStatus(), self.obj.GetDibMsg1()