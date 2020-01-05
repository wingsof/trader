from morning_server import stream_readwriter
from morning_server import message


def request_stock_day_data(reader, code, from_date, until_date, method=message.DAY_DATA):
    header = stream_readwriter.create_header(message.REQUEST, message.MARKET_STOCK, method)
    header['code'] = code
    header['from'] = from_date
    header['until'] = until_date
    body = []
    print(header)
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