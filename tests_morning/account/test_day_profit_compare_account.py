import pytest
from morning.account.day_profit_compare_account import DayProfitCompareAccount
from datetime import date


def test_get_highest_price():
    dpca = DayProfitCompareAccount()
    assert 135300 == dpca.get_highest_price(date(2019, 11, 25), 'A028300', 10000)

    dpca.set_up(3, date(2019, 11, 25))
    dpca.transaction('cybos:A028300:BUY:135000:903000')
    dpca.summary()