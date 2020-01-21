import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import win32com.client
from winapi import connection
import time
from datetime import datetime, timedelta
from utils import time_converter
from pymongo import MongoClient

def check_investor_trend(client, code):
    conn = connection.Connection()
    
    obj = win32com.client.Dispatch('CpSysDib.CpSvr7254')
    obj.SetInputValue(0, code)
    obj.SetInputValue(1, 6)
    obj.SetInputValue(4, ord('0'))
    obj.SetInputValue(5, 0)
    obj.SetInputValue(6, ord('1'))
    client.stock[code + '_INV'].drop()
    now = datetime.now()
    continue_request = True
    prev = None
    while continue_request:
        while conn.request_left_count() <= 0:
            print('Request Limit is reached', flush=True)
            time.sleep(1)
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

            client.stock[code + '_INV'].insert_one(d)

            if now - time_converter.intdate_to_datetime(d['0']) > timedelta(days=365*5):
                continue_request = False
            prev = d
            print(code, 'OK', d['0'])
    print(code, 'DONE')

if __name__ == '__main__':
    from PyQt5.QtCore import QCoreApplication
    import sys
    import stock_code

    code_list = stock_code.get_kospi200_list()
    for code in code_list:
        client = MongoClient('mongodb://192.168.0.22:27017')
        check_investor_trend(client, code)

