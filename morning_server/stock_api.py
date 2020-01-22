from morning_server import stream_readwriter
from morning_server import message


def request_stock_day_data(reader, code, from_date, until_date, method=message.DAY_DATA):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, method)
    header['code'] = code
    header['from'] = from_date
    header['until'] = until_date
    body = []
    #print(header)
    return reader.block_write(header, body)


def request_stock_minute_data(reader, code, from_date, until_date):
    return request_stock_day_data(reader, code, from_date, until_date, message.MINUTE_DATA)


def subscribe_stock(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.STOCK_DATA)
    body = []
    reader.subscribe_write(header, body, code, handler)


def request_stock_code(reader, market_type):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.CODE_DATA)
    header['market_type'] = market_type
    body = []
    return reader.block_write(header, body)


def request_long_list(reader):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.GET_LONG_LIST)
    body = []
    return reader.block_write(header, body)


def order_stock(reader, code, price, quantity, is_buy):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.ORDER_STOCK)
    header['code'] = code
    header['price'] = price
    header['quantity'] = quantity
    header['trade_type'] = message.ORDER_BUY if is_buy else message.ORDER_SELL
    body = []
    return reader.block_write(header, body)

def subscribe_trade(reader, handler):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.TRADE_DATA)
    body = []
    reader.subscribe_trade_write(header, body, handler)

def modify_order(reader, order_num: int, code, price):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.MODIFY_ORDER)
    header['code'] = code
    header['order_number'] = order_num
    header['price'] = price
    body = []
    return reader.block_write(header, body)

def cancel_order(reader, order_num: int, code, amount): # quantity
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.CANCEL_ORDER)
    header['code'] = code
    header['order_number'] = order_num
    header['amount'] = amount
    body = []
    return reader.block_write(header, body)
