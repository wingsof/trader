from pymongo import MongoClient

"""
db = MongoClient('mongodb://192.168.0.22:27017')
with db:
    stock_db = db['stock']
    collections = stock_db.collection_names()
    for c in collections:
        if c.endswith('_M'):
            stock_db[c].drop()
"""