import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..')))


import win32com.client
import time

from morning.logging import logger
from morning.cybos_api import connection


class OrderInQueue:
    def __init__(self, account_num, account_type):
        self.obj = win32com.client.Dispatch('CpTrade.CpTd5339')
        self.obj.SetInputValue(0, account_num)
        self.obj.SetInputValue(1, account_type)
        self.obj.SetInputValue(4, '0')
        self.obj.SetInputValue(6, '0')
        self.obj.SetInputValue(7, 20)
        self.conn = connection.Connection()

    def _td5339(self):
        orders = []
        while True:
            ret = self.obj.BlockRequest()
            print(ret)
            if self.obj.GetDibStatus() != 0:
                logger.error('TD5339 failed')
                return []
            elif ret == 2 or ret == 3:
                logger.error('TD5339 communication failed')
                return []

            while ret == 4:
                if self.conn.request_left_count() <= 0:
                    time.sleep(self.conn.get_remain_time() / 1000)
                ret = self.obj.BlockRequest()
            
            count = self.obj.GetHeaderValue(5)

            for i in range(count):
                order = dict()
                order['number'] = self.obj.GetDataValue(1, i)
                order['prev'] = self.obj.GetDataValue(2, i) # 원주문 번호?
                order['code'] = self.obj.GetDataValue(3, i)
                order['name'] = self.obj.GetDataValue(4, i)
                order['desc'] = self.obj.GetDataValue(5, i)
                order['quantity'] = self.obj.GetDataValue(6, i)
                order['price'] = self.obj.GetDataValue(7, i)
                order['traded_quantity'] = self.obj.GetDataValue(8, i) # 체결수량
                order['credit_type'] = self.obj.GetDataValue(9, i) # 신용구분
                order['edit_available_quantity'] = self.obj.GetDataValue(11, i) #정정취소 가능수량
                order['is_buy'] = self.obj.GetDataValue(13, i) # 매매구분코드
                order['credit_date'] = self.obj.GetDataValue(17, i) # 대출일
                order['flag_describe'] = self.obj.GetDataValue(19, i) # 주문호가구분코드 내용
                order['flag'] = self.obj.GetDataValue(21, i)    # 주문호가구분코드
                logger.print('ORDER IN QUEUE', order)
                orders.append(order)
            if self.obj.Continue == False:
                break
        
        return orders


    def request(self):
        return self._td5339()


if __name__ == '__main__':
    from morning.cybos_api.trade_util import TradeUtil
    tu = TradeUtil()
    oiq = OrderInQueue(tu.get_account_number(), tu.get_account_type())
    print(oiq.request())