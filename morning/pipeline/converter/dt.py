

class MarketType:
    PRE_MARKET_EXP = ord('1')
    IN_MARKET = ord('2')
    PRE_MARKET_CUR = ord('3') # StockOutCur
    AFTER_MARKET = ord('4')
    AFTER_MARKET_EXP = ord('5')


class CybosStockTick:
    CODE = '0'
    COMPANY_NAME = '1'
    YESTERDAY_DIFF = '2'
    TIME = '3'
    START_PRICE = '4'
    HIGHEST_PRICE = '5'
    LOWEST_PRICE = '6'
    ASK_PRICE = '7'
    BID_PRICE = '8'
    CUM_VOLUME = '9'
    CUM_AMOUNT = '10'
    CURRENT_PRICE = '13'
    BUY_OR_SELL = '14'
    CUM_SELL_VOLUME_BY_PRICE = '15' # 체결가 방식
    CUM_BUY_VOLUME_BY_PRICE = '16'
    VOLUME = '17'
    TIME_WITH_SEC = '18'
    MARKET_TYPE_EXP = '19'
    MARKET_TYPE = '20' # 장중에 49 ('1') 나오는 경우 VI 발동 2분동안
    OUT_TIME_VOLUME = '21'
    CUM_SELL_VOLUME = '27'  # 호가 방식
    CUM_BUY_VOLUME = '28'


class CybosStockBidAskTick:
    CODE = '0'
    TIME = '1'
    VOLUME = '2'
    FIRST_ASK_PRICE = '3'
    FIRST_BID_PRICE = '4'
    FIRST_ASK_REMAIN = '5'
    FIRST_BID_REMAIN = '6'
    SECOND_ASK_PRICE = '7'
    SECOND_BID_PRICE = '8'
    SECOND_ASK_REMAIN = '9'
    SECOND_BID_REMAIN = '10'
    THIRD_ASK_PRICE = '11'
    THIRD_BID_PRICE = '12'
    THIRD_ASK_REMAIN = '13'
    THIRD_BID_REMAIN = '14'
    FOURTH_ASK_PRICE = '15'
    FOURTH_BID_PRICE = '16'
    FOURTH_ASK_REMAIN = '17'
    FOURTH_BID_REMAIN = '18'
    FIFTH_ASK_PRICE = '19'
    FIFTH_BID_PRICE = '20'
    FIFTH_ASK_REMAIN = '21'
    FIFTH_BID_REMAIN = '22'
    TOTAL_ASK_REMAIN = '23'
    TOTAL_BID_REMAIN = '24'
    OUT_TIME_TOTAL_ASK_REMAIN = '25'
    OUT_TIME_TOTAL_BID_REMAIN = '26'


class CybosStockDayTick:
    #DATE = '0'
    TIME = '1' # hhmm
    START_PRICE = '2'
    HIGHEST_PRICE = '3'
    LOWEST_PRICE = '4'
    CLOSE_PRICE = '5'
    VOLUME = '6'
    AMOUNT = '7'
    CUM_SELL_VOLUME = '8'
    CUM_BUY_VOLUME = '9'
    FOREIGNER_HOLD_VOLUME = '10'
    FOREIGNER_HOLD_RATE = '11'
    INSTITUTION_BUY_VOLUME = '12'
    INSTITUTION_CUM_BUY_VOLUME = '13'


class CybosStockInvestor:
    INDIVIDUAL = '1'
    FOREIGNER = '2'
    ORGANIZATION = '3'
    FINANCE_INVEST = '4'
    INSURANCE = '5'
    COLLECTIVE_INVEST = '6'
    BANK = '7'
    ETC_INVEST = '8'
    PENSION = '9'
    ETC_ORGANIZATION = '10'
    ETC_FOREIGNER = '11'
    PRIVATE_EQUITY = '12'
    NATIONAL_ORGANIZATION = '13'
    CLOSE_PRICE = '14'
    YESTERDAY_DIFF = '15'
    YESTERDAY_DIFF_RATE = '16'
    VOLUME = '17'
    IS_ESTIMATE = '18' # 0: estimate, 1: confirm

stock_tick = {}
stock_ba_tick = {}
stock_day_tick = {}
investor_tick = {}

for k, v in vars(CybosStockTick).items():
    if not k.startswith('_'):
        stock_tick[v] = k.lower()

for k, v in vars(CybosStockBidAskTick).items():
    if not k.startswith('_'):
        stock_ba_tick[v] = k.lower()

for k, v in vars(CybosStockDayTick).items():
    if not k.startswith('_'):
        stock_day_tick[v] = k.lower()

for k, v in vars(CybosStockInvestor).items():
    if not k.startswith('_'):
        investor_tick[v] = k.lower()


def cybos_stock_tick_convert(raw_data):
    converted = {}
    for k, v in raw_data.items():
        if k in stock_tick:
            converted[stock_tick[k]] = v
        else:
            converted[k] = v
    return converted


def cybos_stock_ba_tick_convert(raw_data):
    converted = {}
    for k, v in raw_data.items():
        if k in stock_ba_tick:
            converted[stock_ba_tick[k]] = v
        else:
            converted[k] = v
    return converted


def cybos_stock_day_tick_convert(raw_data):
    converted = {}
    for k, v in raw_data.items():
        if k in stock_day_tick:
            converted[stock_day_tick[k]] = v
        else:
            converted[k] = v
    return converted


def cybos_stock_investor_convert(raw_data):
    converted = {}
    for k, v in raw_data.items():
        if k in investor_tick:
            converted[investor_tick[k]] = v
        else:
            converted[k] = v
    return converted
