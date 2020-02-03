import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import client_info

HOME_MONGO_ADDRESS = ('mongodb://' + client_info.get_mongo_id() + ':' + 
                        client_info.get_mongo_password() + '@' + 
                        client_info.get_server_ip() + ':27017')


def tr_code(code):
    special_code = {'.DJI': 'DJI',
                    'JP#NI225': 'JPNI225',
                    '399102': 'U399102',
                    'CZ#399106': 'CZ399106',
                    '95079': 'U95079',
                    'HK#HS': 'HKHS',
                    'GR#DAX': 'GR#DAX'}
    if code in special_code:
        return special_code[code]

    return code


if __name__ == '__main__':
    print(HOME_MONGO_ADDRESS)
