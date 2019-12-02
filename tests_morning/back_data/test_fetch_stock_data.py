import pytest
from morning.back_data.fetch_stock_data import _insert_day_data
from datetime import date

def test_fetch_stock_data():
    working_days = [
        date(2019, 1, 1), date(2019, 1, 2), date(2019, 1, 3), date(2019, 1, 4),
        date(2019, 1, 5), date(2019, 1, 6)
    ]

    days1 = [
        date(2019, 1, 1), date(2019, 1, 2), date(2019, 1, 3), date(2019, 1, 4),
        date(2019, 1, 5), date(2019, 1, 6)
    ]

    days2 = [
        date(2019, 1, 1), date(2019, 1, 2)
    ]

    days3 = [
        date(2019, 1, 5), date(2019, 1, 6)
    ]

    days4 = [
        date(2019, 1, 1), date(2019, 1, 2),
        date(2019, 1, 5), date(2019, 1, 6)
    ]

    days5 = [
        date(2019, 1, 1), date(2019, 1, 2), date(2019, 1, 3),
        date(2019, 1, 5), date(2019, 1, 6)
    ]

    days6 = []

    r = _insert_day_data(None, '', days1, working_days, '')
    assert len(r) == 0

    r = _insert_day_data(None, '', days2, working_days, '')
    assert r == [(date(2019, 1, 3), date(2019, 1, 6))]

    r = _insert_day_data(None, '', days3, working_days, '')
    assert r == [(date(2019, 1, 1), date(2019, 1, 4))]

    r = _insert_day_data(None, '', days4, working_days, '')
    assert r == [(date(2019, 1, 3), date(2019, 1, 4))]

    r = _insert_day_data(None, '', days5, working_days, '')
    assert r == [(date(2019, 1, 4), date(2019, 1, 4))]

    r = _insert_day_data(None, '', days6, working_days, '')
    assert r == [(date(2019, 1, 1), date(2019, 1, 6))]