import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from dbapi import config


def get_kospi200_list():
    client = MongoClient(config.MONGO_SERVER)
    collection = client.stock.kospi200_code
    codes = list(collection.find({}))

    return list(map(lambda x: x['code'], codes))

def is_there_warning(code):
    return False


    """
    def get_kospi_code_list():
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockListByMarket(1)

    def get_kosdaq_code_list():
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockListByMarket(2)

    def is_kospi_200(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockKospi200Kind(code)

    def is_company_stock(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockSectionKind(code) == 1

    def get_country_code():
        obj = win32com.client.Dispatch('CpUtil.CpUsCode')
        return obj.GetUsCodeList(2)

    def get_us_name(code):
        obj = win32com.client.Dispatch('CpUtil.CpUsCode')
        return obj.GetNameByUsCode(code)

    def code_to_name(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.CodeToName(code)

    def is_there_warning(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockControlKind (code) > 0 or obj.GetStockStatusKind(code) > 0 or obj.GetStockSupervisionKind(code) > 0

    def get_industry_name(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetIndustryName(obj.GetStockIndustryCode(code))

    def get_us_code():
        obj = win32com.client.Dispatch("CpUtil.CpUsCode")
        return obj.GetUsCodeList(1)
    """

if __name__ == '__main__':
    print("KOSPI ", get_kospi200_list())
