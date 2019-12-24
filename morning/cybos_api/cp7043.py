import win32com.client


class Cp7043:
    MAX_CODE_COUNT = 20
    KOSPI = 0
    KOSDAQ = 1
    # KOSDAQ FIXED
    def __init__(self, market):
        self.objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7043")
        if market == Cp7043.KOSPI:
            self.objRq.SetInputValue(0, ord('1')) # 코스닥
        else:
            self.objRq.SetInputValue(0, ord('2')) # 코스닥
        # 1 값에 값을 넣는 경우, 상승한 종목만 걸러냄
        self.objRq.SetInputValue(1, ord('2'))  # 상승()
        self.objRq.SetInputValue(2, ord('1'))  # 당일
        self.objRq.SetInputValue(3, 61)  # 거래대금 상위순
        self.objRq.SetInputValue(4, ord('2'))  # 관리 종목 포함
        self.objRq.SetInputValue(5, ord('0'))  # 거래량 구분 "전체"
        self.objRq.SetInputValue(6, ord('0'))  # '표시 항목 선택 - '0': 시가대비
        self.objRq.SetInputValue(7, 0)  #  등락율 시작
        self.objRq.SetInputValue(8, 15)  # 등락율 끝
 
    def _rq7043(self, retcode):
        self.objRq.BlockRequest()
        rqStatus = self.objRq.GetDibStatus()

        if rqStatus != 0:
            print("Connection Status", rqStatus)
            return False
 
        cnt = self.objRq.GetHeaderValue(0)
        cntTotal  = self.objRq.GetHeaderValue(1)
        #print(cnt, cntTotal)
 
        for i in range(cnt):
            code = self.objRq.GetDataValue(0, i)  # 코드
            retcode.append(code)

            if len(retcode) >=  Cp7043.MAX_CODE_COUNT:       # 최대 10 종목만,
                break
            name = self.objRq.GetDataValue(1, i)  # 종목명
            diffflag = self.objRq.GetDataValue(3, i)
            diff = self.objRq.GetDataValue(4, i)
            vol = self.objRq.GetDataValue(6, i)  # 거래량
            #print(code, name, diffflag, diff, vol)

 
    def request(self, codes_in):
        self._rq7043(codes_in)
 
        if len(codes_in) < Cp7043.MAX_CODE_COUNT:
            while self.objRq.Continue:
                self._rq7043(codes_in)

                if len(codes_in) >= Cp7043.MAX_CODE_COUNT:
                    print('break')
                    break
        
        return True


if __name__ == '__main__':
    import stock_code
    cp7043 = Cp7043(Cp7043.KOSDAQ)
    codes = []
    cp7043.request(codes)
    print(len(codes))
    print(len(set(codes)))
    print(codes)
    duplicated = 0
    for code in codes:
        matched = 0
        for c in codes:
            if c == code:
                matched += 1
        if matched > 1:
            duplicated += 1
            print('duplicated', code, matched)

    for code in set(codes):
        if not stock_code.is_company_stock(code):
            print('code is not company stock', code)