import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..' + os.sep + '..')))

import win32com.client
from utils import time_converter
from datetime import datetime, timedelta
from cybos_api import connection
import gevent
from utils import rlogger


def get_today_data_raw(code, period_type='m'):
    data = []
    conn = connection.Connection()
    conn.wait_until_available()

    chart_obj= win32com.client.Dispatch("CpSysDib.StockChart")
    chart_obj.SetInputValue(0, code)
    chart_obj.SetInputValue(1, ord('2'))
    chart_obj.SetInputValue(4, 360)
    data_list = [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 16, 17, 20, 21, 6, 37]
    chart_obj.SetInputValue(5, data_list)
    chart_obj.SetInputValue(6, ord(period_type))
    chart_obj.SetInputValue(9, ord('0'))
    chart_obj.SetInputValue(10, ord('1'))
    chart_obj.BlockRequest()

    data_len = chart_obj.GetHeaderValue(3)
    for i in range(data_len):
        d = {}
        for j in range(len(data_list)):
            d[str(j)] = chart_obj.GetDataValue(j, i)
        data.append(d)

    print('GET TODAY', data)
    return len(data), reversed(data)


def get_today_min_data(code):
    result_len, result = get_today_data_raw(code)
    return result_len, list(result)

def get_today_tick_data(code):
    result_len, result = get_today_data_raw(code, 'T')
    return result_len, list(result)
