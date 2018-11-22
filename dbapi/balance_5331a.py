from pymongo import MongoClient

_MONGO_SERVER = 'mongodb://nnnlife.iptime.org:27017'
_COLLECTION = 'balance'

def _create_balance(account_num, account_type, db):
    b = {'account_num': account_num, 'account_type': account_type,  'balance': 10000000}
    db[_COLLECTION].insert_one(b)


def get_balance(account_num, account_type):
    db = MongoClient(_MONGO_SERVER).trader

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


if __name__ == '__main__':
    db = MongoClient(_MONGO_SERVER).trader
    b = get_balance('test', 'test')
    db[_COLLECTION].update_one({'account_num': 'test', 'account_type': 'test'}, {'$set': {'balance': b-1}}, upsert=False)
    assert get_balance('test', 'test') == b-1
