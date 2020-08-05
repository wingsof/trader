import stock_provider_pb2 as stock_provider
from google.protobuf.empty_pb2 import Empty
import simulstatus


_balance = 1000000
TAX_RATE = 0.0025
_stub = None


def get_balance():
    if simulstatus.is_simulation():
        return _balance

    if _stub is None:
        return 0

    balance = _stub.GetBalance(Empty())
    return balance.balance


def pay_for_stock(amount, use_tax=True):
    global _balance

    if simulstatus.is_simulation():
        if amount < 0.0 and use_tax:
            amount = amount * (1 - TAX_RATE)

        _balance -= amount
        _balance = int(_balance)
        print('CURRENT ACCOUNT: ', _balance, amount)


def set_simulation(is_simulation):
    global _balance

    if simulstatus.is_simulation():
        _balance = 1000000



simulstatus.add_handler(set_simulation)
