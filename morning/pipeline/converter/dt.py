

class MarketType:
    PRE_MARKET_EXP = '1'
    IN_MARKET = '2'
    PRE_MARKET_CUR = '3' # StockOutCur
    AFTER_MARKET = '4'
    AFTER_MARKET_EXP = '5'


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
    CUM_SELL_VOLUME = '15'
    CUM_BUY_VOLUME = '16'
    VOLUME = '17'
    TIME_WITH_SEC = '18'
    MARKET_TYPE_EXP = '19'
    MARKET_TYPE = '20'
    OUT_TIME_VOLUME = '21'


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


stock_tick = {}
stock_ba_tick = {}

for k, v in vars(CybosStockTick).items():
    if not k.startswith('_'):
        stock_tick[v] = k.lower()

for k, v in vars(CybosStockBidAskTick).items():
    if not k.startswith('_'):
        stock_ba_tick[v] = k.lower()


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
