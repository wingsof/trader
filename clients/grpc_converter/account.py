import stock_provider_pb2 as stock_provider
from google.protobuf.empty_pb2 import Empty
import simulstatus


_balance = 10000000


def get_balance(stub):
    if simulstatus.is_simulation():
        return _balance

    balance = stub.GetBalance(Empty())
    return balance.balance


def pay_for_stock(amount):
    global _balance

    if simulstatus.is_simulation():
        _balance -= amount


def set_simulation(is_simulation):
    global _balance

    if simulstatus.is_simulation():
        _balance = 10000000



simulstatus.add_handler(set_simulation)
