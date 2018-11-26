import win32com.client


class StockCode:
    @staticmethod
    def get_kospi_code_list():
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockListByMarket(1)

    @staticmethod
    def get_kosdaq_code_list():
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockListByMarket(2)

    @staticmethod
    def is_kospi_200(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockKospi200Kind(code)

    @staticmethod
    def is_company_stock(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockSectionKind(code) == 1

    @staticmethod
    def get_country_code():
        obj = win32com.client.Dispatch('CpUtil.CpUsCode')
        return obj.GetUsCodeList(2)

    @staticmethod
    def get_us_name(code):
        obj = win32com.client.Dispatch('CpUtil.CpUsCode')
        return obj.GetNameByUsCode(code)

    @staticmethod
    def get_kospi200_list():
        kospi_200 = []
        code_list = StockCode.get_kospi_code_list()
        for code in code_list:
            if StockCode.is_kospi_200(code) > 0:
                kospi_200.append(code)
        return kospi_200

    @staticmethod
    def code_to_name(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.CodeToName(code)

    @staticmethod
    def is_there_warning(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetStockControlKind (code) > 0 or obj.GetStockStatusKind(code) > 0 or obj.GetStockSupervisionKind(code) > 0

    @staticmethod
    def get_industry_name(code):
        obj = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        return obj.GetIndustryName(obj.GetStockIndustryCode(code))

    @staticmethod
    def get_us_code():
        obj = win32com.client.Dispatch("CpUtil.CpUsCode")
        return obj.GetUsCodeList(1)

if __name__ == '__main__':
    import connection

    conn = connection.Connection()
    print("Connected", conn.is_connected())
    print("Left", conn.request_left_count())
    print("KOSPI ", StockCode.get_kospi_code_list())
    print("Warning", StockCode.is_there_warning('A134780'))
    print("Left", conn.request_left_count())
    print("GroupName", StockCode.get_industry_name('A032640'))

    print("US CODE ALL", StockCode.get_us_code())
    country_code = StockCode.get_country_code()
    for code in country_code:
        print(code, StockCode.get_us_name(code))
