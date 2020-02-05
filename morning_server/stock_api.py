from datetime import datetime, timedelta

from morning_server import stream_readwriter
from morning_server import message


def request_stock_day_data(reader, code, from_date, until_date, method=message.DAY_DATA):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, method)
    header['code'] = code
    header['from'] = from_date
    header['until'] = until_date
    body = []
    return reader.block_write(header, body)


def request_investor_data(reader, code, from_date, until_date):
    now = datetime.now().date()
    if now - from_date > timedelta(days=365):
        print('over before one year data is not available')
        return []

    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.INVESTOR_DATA)
    header['code'] = code
    header['from'] = from_date
    header['until'] = until_date
    body = []
    return reader.block_write(header, body)


def request_abroad_data(reader, code, period_type, count):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.ABROAD_DATA)
    header['code'] = code
    header['period_type'] = period_type
    header['count'] = count
    body = []
    return reader.block_write(header, body)


def request_stock_minute_data(reader, code, from_date, until_date):
    return request_stock_day_data(reader, code, from_date, until_date, message.MINUTE_DATA)


def subscribe_stock(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.STOCK_DATA)
    body = []
    reader.subscribe_write(header, body, code, handler)


def subscribe_stock_bidask(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.BIDASK_DATA)
    body = []
    code += message.BIDASK_SUFFIX
    reader.subscribe_write(header, body, code, handler)


def subscribe_stock_subject(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.SUBJECT_DATA)
    body = []
    code += message.SUBJECT_SUFFIX
    reader.subscribe_write(header, body, code, handler)


def subscribe_world(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.WORLD_DATA)
    body = []
    code += message.WORLD_SUFFIX
    reader.subscribe_write(header, body, code, handler)


def subscribe_index(reader, code, handler):
    header = stream_readwriter.create_header(message.SUBSCRIBE, message.MARKET_STOCK, message.INDEX_DATA)
    body = []
    code += message.INDEX_SUFFIX
    reader.subscribe_write(header, body, code, handler)


def request_stock_code(reader, market_type):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.CODE_DATA)
    header['market_type'] = market_type
    body = []
    return reader.block_write(header, body)


def request_us_stock_code(reader, us_type):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, message.USCODE_DATA)
    header['us_type'] = us_type
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


def request_order_in_queue(reader):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.ORDER_IN_QUEUE)
    body = []
    return reader.block_write(header, body)


def get_balance(reader):
    header = stream_readwriter.create_header(message.REQUEST_TRADE, message.MARKET_STOCK, message.BALANCE)
    body = []
    return reader.block_write(header, body)
