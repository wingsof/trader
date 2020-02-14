from pymongo import MongoClient

import sys, signal


db = MongoClient('mongodb://' + sys.argv[1] + ':' + sys.argv[2] + '@192.168.0.22:27017')
with db:
    stock_db = db['trade_alarm']
    collections = stock_db.collection_names()
    for c in collections:
        if c.startswith('A') or c == 'alarm' or c== 'test':
            stock_db[c].drop()
        else:
            print(c)
