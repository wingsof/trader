import stock_chart
from datetime import datetime
import stock_code
from pymongo import MongoClient
import win32com.client
import time_converter

def insert_investor_trend(client, code):
    obj = win32com.client.Dispatch('CpSysDib.CpSvr7254')
    obj.SetInputValue(0, code)
    obj.SetInputValue(1, 6)
    obj.SetInputValue(4, ord('0'))
    obj.SetInputValue(5, 0)
    obj.SetInputValue(6, ord('1'))

    obj.BlockRequest()
    count = obj.GetHeaderValue(1)
    today = datetime.now()

    for i in range(count):
        d = {}
        for j in range(19):
            d[str(j)] = obj.GetDataValue(j, i)
        t = time_converter.intdate_to_datetime(d['0'])
        if t.year == today.year and t.month == today.month and t.day == today.day:
            cursor = client.stock[code + '_INV'].find({'0': d['0']})
            if cursor.count() == 0:
                client.stock[code + '_INV'].insert_one(d)


def insert_short_cover(client, code):    
    obj = win32com.client.Dispatch('CpSysDib.CpSvr7240')
    obj.SetInputValue(0, code)

    obj.BlockRequest()
    count = obj.GetHeaderValue(0)
    today = datetime.now()

    for i in range(count):
        d = {}
        for j in range(11):
            d[str(j)] = obj.GetDataValue(j, i)

        t = time_converter.intdate_to_datetime(d['0'])
        if t.year == today.year and t.month == today.month and t.day == today.day:
            cursor = client.stock[code + '_COVER'].find({'0': d['0']})
            if cursor.count() == 0:
                client.stock[code + '_COVER'].insert_one(d)


def daily_insert_data():
    start_date = datetime(2013, 1, 1)
    end_date = datetime.now()

    code_list = stock_code.StockCode.get_kospi200_list()
    client = MongoClient('mongodb://192.168.0.22:27017')

    for code in code_list:
        l, data = stock_chart.get_day_period_data(code, start_date, end_date)
        client.stock[code + '_D'].drop()
        client.stock[code + '_D'].insert_many(data)
        insert_investor_trend(client, code)
        insert_short_cover(client, code)


if __name__ == '__main__':
    daily_insert_data()