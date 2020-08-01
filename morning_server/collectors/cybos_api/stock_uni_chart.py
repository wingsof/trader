import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..' + os.sep + '..' + os.sep + '..')))

import win32com.client
from utils import time_converter
from datetime import datetime, timedelta
from morning_server.collectors.cybos_api import connection


def get_uni_data(code):
    conn = connection.Connection()
    conn.wait_until_available()

    chart_obj= win32com.client.gencache.EnsureDispatch("CpSysDib.StockUniMst")
    chart_obj.SetInputValue(0, code)
    chart_obj.BlockRequest()

    d = {}
    for i in range(139):
        d[str(i)] = chart_obj.GetHeaderValue(i)

    return [d]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(get_uni_data(sys.argv[1]))
    else:
        print('Usage)', sys.argv[0], 'code')
