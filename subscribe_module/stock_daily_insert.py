import stock_chart
from datetime import datetime
import stock_code
from pymongo import MongoClient


def daily_insert_data():
    start_date = datetime(2013, 1, 1)
    end_date = datetime.now()

    code_list = stock_code.StockCode.get_kospi200_list()
    client = MongoClient('mongodb://192.168.0.22:27017')

    for code in code_list:
        l, data = stock_chart.get_day_period_data(code, start_date, end_date)
        client.stock[code + '_D'].drop()
        client.stock[code + '_D'].insert_many(data)