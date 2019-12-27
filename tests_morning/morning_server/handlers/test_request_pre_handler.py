import pytest

from morning_server.handlers import request_pre_handler
from datetime import date, datetime, timedelta


def test_check_empty_date():
    days = [date(2019, 3, 4)]
    working = [date(2019, 3, 4)]
    assert len(request_pre_handler._check_empty_date(days, [], working)) == 0

    days = []
    working = []
    assert len(request_pre_handler._check_empty_date(days, [], working)) == 0

    days = [date(2019, 3, 4)]
    working = [date(2019, 3, 4), date(2019, 3, 5), date(2019, 3, 6)]
    assert request_pre_handler._check_empty_date(days, [], working) == [(date(2019, 3, 5), date(2019, 3, 6))]

    days = [date(2019, 3, 5)]
    working = [date(2019, 3, 4), date(2019, 3, 5), date(2019, 3, 6)]
    assert request_pre_handler._check_empty_date(days, [], working)  == [(date(2019, 3, 4), date(2019, 3, 4)), (date(2019, 3, 6), date(2019, 3, 6))]

    days = [date(2019, 3, 6)]
    working = [date(2019, 3, 4), date(2019, 3, 5), date(2019, 3, 6)]
    assert request_pre_handler._check_empty_date(days, [], working) == [(date(2019, 3, 4), date(2019, 3, 5))]

def test_check_empty_date_with_vacancy():
    days = [date(2019, 3, 4)]
    vacancy_days = [date(2019, 3, 5)]
    working = [date(2019, 3, 4), date(2019, 3, 5), date(2019, 3, 6)]
    assert request_pre_handler._check_empty_date(days, vacancy_days, working) == [(date(2019, 3, 6), date(2019, 3, 6))]

    days = [date(2019, 3, 5)]
    working = [date(2019, 3, 3), date(2019, 3, 4), date(2019, 3, 5), date(2019, 3, 6)]
    vacancy_days = [date(2019, 3, 4)]
    assert request_pre_handler._check_empty_date(days, vacancy_days, working)  == [(date(2019, 3, 3), date(2019, 3, 3)), (date(2019, 3, 6), date(2019, 3, 6))]

def test_correct_date():
    assert request_pre_handler._correct_date(date(2019, 12, 30), datetime(2019, 12, 27, 12)) == date(2019, 12, 26)
    assert request_pre_handler._correct_date(date(2019, 12, 27), datetime(2019, 12, 27, 19)) == date(2019, 12, 27)

def test_get_data_from_db():
    pass
    #print(request_pre_handler._get_data_from_db('A005930', date(2019, 12, 9), date(2019, 12, 27), '_D'))

def test_sort_db_data():
    data = [{'0': 20191201, '1': 1003}, {'0': 20191201, '1': 940}, {'0': 20191127, '1': 900}]
    assert request_pre_handler.sort_db_data(data, '_M') == [{'0': 20191127, '1': 900}, {'0': 20191201, '1': 940}, {'0': 20191201, '1': 1003}]
    assert request_pre_handler.sort_db_data(data, '_D') != [{'0': 20191127, '1': 900}, {'0': 20191201, '1': 940}, {'0': 20191201, '1': 1003}]
    assert request_pre_handler.sort_db_data(data, '_D') == [{'0': 20191127, '1': 900}, {'0': 20191201, '1': 1003}, {'0': 20191201, '1': 940}]
