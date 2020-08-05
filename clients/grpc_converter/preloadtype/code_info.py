from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
from datetime import datetime, timedelta
from clients.common import morning_client


_code_info = {}


class CodeInfo:
    def __init__(self, corp_name, is_kospi):
        self.corp_name = corp_name
        self.is_kospi = is_kospi


def load_code_info(codes):
    for progress, code in enumerate(codes):
        print('collect code_info', f'{progress+1}/{len(codes)}', end='\r')
        corp_name = morning_client.code_to_name(code)
        is_kospi = morning_client.is_kospi_code(code)
        _code_info[code] = CodeInfo(corp_name, is_kospi)

    print('')


def is_kospi(code):
    if code in _code_info:
        return _code_info[code].is_kospi
    return False


def get_corp_name(code):
    if code in _code_info:
        return _code_info[code].corp_name
    return ''
