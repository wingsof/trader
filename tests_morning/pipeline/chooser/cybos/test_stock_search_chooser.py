import pytest

from morning.pipeline.chooser.cybos.db.stock_search_bull_chooser import StockSearchBullChooser
from datetime import date
import pandas as pd
from pymongo import MongoClient
from morning.config import db
from morning.back_data.holidays import is_holidays, get_yesterday
import platform


def get_bull_codes_by_manual(my_date, count, code_collection):
    from morning.back_data.fetch_stock_data import get_day_period_data
    stock = MongoClient(db.HOME_MONGO_ADDRESS)['stock']
    codes = list(stock[code_collection].find())
    remote_codes = []
    for code in codes:
        remote_codes.append(code['code'])
    yesterday = get_yesterday(my_date)
    datas = []
    for code in remote_codes:
        data = get_day_period_data(code, yesterday, yesterday)
        if len(data) > 0:
            data[0]['code'] = code
            datas.append(data[0])

    datas = sorted(datas, key=lambda i: i['7'], reverse=True)
    codes = [d['code'] for d in datas]
    return codes[:count]

def test_verify_kospi_bull():
    if platform.system() != 'Windows':
        return

    my_date = date(2019, 12, 19)
    ssbc = StockSearchBullChooser(StockSearchBullChooser.KOSDAQ, my_date, True, 0)
    mcodes = get_bull_codes_by_manual(my_date, 80, 'KOSDAQ_CODES')
    assert ssbc.codes == mcodes

    ssbc = StockSearchBullChooser(StockSearchBullChooser.KOSPI, my_date, True, 0)
    mcodes = get_bull_codes_by_manual(my_date, 80, 'KOSPI_CODES')
    assert ssbc.codes == mcodes