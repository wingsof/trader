import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..' + os.sep + '..')))


import pytest
from morning.account.order.order_transaction import OrderTransaction
from morning.account.cybos_kosdaq_account import CybosKosdaqAccount
from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSlot, QObject

class MockOrder(QObject):
    def __init__(self, accout_num, account_type, listener):
        super().__init__()
        self.last_process = None
        self.listener = listener

    def stop(self):
        pass

    @pyqtSlot()
    def traded_send_event(self):
        result = {
            'flag': '1',
            'code': self.last_process['code'],
            'order_number': 12345,
            'quantity': self.last_process['quantity'],
            'price': self.last_process['price'],
            'order_type': '2' if self.last_process['is_buy'] else '1',
            'total_quantity': self.last_process['quantity']
        }
        self.listener.order_event(result)

    @pyqtSlot()
    def queue_send_event(self):
        print('SEND EVENT')
        result = {
            'flag': '4',
            'code': self.last_process['code'],
            'order_number': 12345,
            'quantity': self.last_process['quantity'],
            'price': self.last_process['price'],
            'order_type': '2' if self.last_process['is_buy'] else '1',
            'total_quantity': self.last_process['quantity']
        }
        self.listener.order_event(result)

    def process(self, code, quantity, account_num, account_type, price, is_buy):
        print('PROCESS')
        self.last_process = dict(code=code, quantity=quantity, account_num=account_num,
                                    account_type=account_type, price=price, is_buy=is_buy)
        QTimer.singleShot(1000, self.queue_send_event)
        QTimer.singleShot(1500, self.traded_send_event)
        return 0, 'OK'


class MockAccount:
    def __init__(self):
        pass

    def get_ask_price(self, code, n_th):
        return 1000


#def test_make_order():
app = QCoreApplication([])

mock_account = MockAccount()
order_transaction = OrderTransaction(mock_account)
mock_order = MockOrder(order_transaction.account_num, order_transaction.account_type, order_transaction)
order_transaction.order = mock_order    # replace order object

order_transaction.make_order('A000010', 1000, 10, True)
assert mock_order.last_process['code'] == 'A000010'
assert mock_order.last_process['quantity'] == 10


QTimer.singleShot(3000, app.exit)

app.exec()
assert len(order_transaction.order_wait_queue) == 0
assert len(order_transaction.on_market_queue) == 0
assert order_transaction.long_list['A000010'] == 10
