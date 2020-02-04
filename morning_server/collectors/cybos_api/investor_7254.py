import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import win32com.client
from datetime import datetime, timedelta
from utils import time_converter
from cybos_api import connection


def check_investor_trend(code, max_count):
    conn = connection.Connection()
    obj = win32com.client.Dispatch('CpSysDib.CpSvr7254')
    obj.SetInputValue(0, code)
    obj.SetInputValue(1, 6)
    obj.SetInputValue(4, ord('0'))
    obj.SetInputValue(5, 0)
    obj.SetInputValue(6, ord('1'))
    now = datetime.now()
    continue_request = True
    datas = []
    prev = None
    while continue_request:
        conn.wait_until_available()
        obj.BlockRequest()
        count = obj.GetHeaderValue(1)

        if count == 0:
            break
        for i in range(count):
            d = {}
            for j in range(19):
                d[str(j)] = obj.GetDataValue(j, i)
            
            if prev != None and prev['0'] < d['0']:
                continue_request = False
                break
            
            if now - time_converter.intdate_to_datetime(d['0']) > timedelta(days=365*5):
                continue_request = False
            prev = d
            datas.append(d)

            if len(datas) >= max_count:
                continue_request = False
                break

    datas = sorted(datas, key=lambda x: x['0'])
    return datas
