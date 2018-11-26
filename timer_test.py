from datetime import datetime
from pymongo import MongoClient
from dbapi import stock_code

client = MongoClient('mongodb://nnnlife.iptime.org:27017')

code_list = stock_code.get_kospi200_list()

for code in code_list:
    client.stock[code].delete_many({
        'date': {'$gte': datetime(2018, 11, 26, 8, 0, 0), '$lte': datetime(2018, 11, 26, 8, 35, 0)}
    })  