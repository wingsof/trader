import datetime

from pymongo import MongoClient
from winapi import stock_code

if __name__ == '__main__':
    
    code_list = stock_code.get_kospi200_list()
    client = MongoClient('mongodb://192.168.0.22:27017')
    for code in code_list:
        client.stock.kospi200_code.insert_one({'code':code})
  