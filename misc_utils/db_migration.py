
from pymongo import MongoClient


if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from dbapi import stock_code

    src = MongoClient('mongodb://nnnlife.iptime.org:27017')
    dest = MongoClient('mongodb://127.0.0.1:27017')

    if 'kospi200_code' not in dest.stock.collection_names():
        collection = src.stock.kospi200_code
        codes = list(collection.find({}))
        for code in codes:
            code.pop('_id', None)
            dest.stock.kospi200_code.insert_one(code)


    daily_collections = filter(lambda x: x.endswith('_D'), src.stock.collection_names())
    for d in daily_collections:
        if d in dest.stock.collection_names():
            dest.stock[d].drop()

        data = list(src.stock[d].find({}))
        for e in data:
            e.pop('_id', None)
        dest.stock[d].insert_many(data)
