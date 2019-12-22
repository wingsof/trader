import pytest
from morning.back_data.holidays import *
from datetime import date

def test_get_yesterday():
    today = date(2019, 12, 9)
    assert date(2019, 12, 6) == get_yesterday(today)

    today = date(2019, 6, 7)
    assert date(2019, 6, 5) == get_yesterday(today)

    today = date(2019, 12, 10)
    assert date(2019, 12, 9) == get_yesterday(today)

    today = date(2018, 5, 2)
    assert date(2018, 4, 30) == get_yesterday(today)