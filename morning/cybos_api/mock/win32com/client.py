


class _CpTd0311: 
    """
        ORDER Object
    """
    def SetInputValue(self, i, value):
        pass

    def BlockRequest(self):
        pass

    def GetDibStatus(self):
        return 0

    def GetDibMsg1(self):
        return 'OK'


class _CpTd5339: 
    """
        Current Order List Object
    """
    Continue=False
    def SetInputValue(self, i, value):
        pass

    def BlockRequest(self):
        pass

    def GetDibStatus(self):
        return 0

    def GetDataValue(self, i, n_th):
        pass

    def GetDibMsg1(self):
        return 'OK'


class _CpCybos:
    LimitRequestRemainTime=0
    def GetLimitRemainCount(self, _):
        return 1000

    def IsConnect(self):
        return True


class _CpTdUtil:
    AccountNumber = [123456, 0]
    def TradeInit(self, i):
        return 0

    def GoodsList(self, account_num, index):
        return ['49', '49']


class _CpConclusion:



def Dispatch(obj_name):
    handlers = dict()
    handlers['CpTrade.CpTd5339'] = _CpTd5339()
    handlers['CpUtil.CpCybos'] = _CpCybos()
    handlers['CpTrade.CpTdUtil'] = _CpTdUtil()
    handlers['CpTrade.CpTd0311'] = _CpTd0311()
    handlers['DsCbo1.CpConclusion'] = _CpConclusion()

    return handlers[obj_name]


def WithEvents(obj, _event_receive_class):
    pass

