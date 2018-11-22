import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from dbapi import config

_COLLECTION = 'balance'

def _create_balance(account_num, account_type, db):
    b = {'account_num': account_num, 'account_type': account_type,  'balance': 10000000}
    db[_COLLECTION].insert_one(b)


def get_balance(account_num, account_type):
    db = MongoClient(config.MONGO_SERVER).trader

    default_balance = 10000000
    if 'balance' not in db.collection_names():
        _create_balance(account_num, account_type, db)
        return default_balance

    cursor = db[_COLLECTION].find({
        'account_num': account_num,
        'account_type': account_type
    })

    print(cursor.count())
    if cursor.count() is 0:
        _create_balance(account_num, account_type, db)
        return default_balance

    b = list(cursor)[0]
    return b[_COLLECTION]

def update_balance(account_num, balance):
    db = MongoClient(config.MONGO_SERVER).trader
    db[_COLLECTION].update_one({'account_num': account_num}, {'$set': {'balance': balance}}, upsert=False)

if __name__ == '__main__':
    db = MongoClient(config.MONGO_SERVER).trader
    b = get_balance('test', 'test')
    db[_COLLECTION].update_one({'account_num': 'test', 'account_type': 'test'}, {'$set': {'balance': b-1}}, upsert=False)
    assert get_balance('test', 'test') == b-1
