# Server Info
CLIENT_SOCKET_PORT = 27019
CLIENT_WEB_PORT = 5000
SERVER_IP = '192.168.0.22'

# Type
REQUEST='request'
RESPONSE='response'
SUBSCRIBE='subscribe'
COLLECTOR='collector'
SUBSCRIBE_RESPONSE='sresponse'
REQUEST_TRADE='request_trade'
RESPONSE_TRADE='response_trade'
TRADE_SUBSCRIBE_RESPONSE='trade_sresponse'

# Market
MARKET_STOCK = 'stock'


# Method
DAY_DATA = 'day_data'
MINUTE_DATA = 'minute_data'
CODE_DATA = 'code_data'
GET_LONG_LIST = 'long_list'
ORDER_STOCK = 'order_stock'
MODIFY_ORDER = 'modify_order'
CANCEL_ORDER = 'cancel_order'
SUBSCRIBE_ORDER = "subscribe_order"

STOCK_DATA = 'stock_realtime'
BIDASK_DATA = 'bidask_realtime'
STOP_STOCK_DATA = 'stock_stop_realtime'
STOP_BIDASK_DATA = 'bidask_stop_realtime'
BACK_DATA = 'stock_backdata'
COLLECTOR_DATA = 'collector_data'
TRADE_DATA = 'trade_realtime'

# Capability
CAPABILITY_REQUEST_RESPONSE=1
CAPABILITY_COLLECT_SUBSCRIBE=2
CAPABILITY_TRADE=4


ORDER_BUY = 2
ORDER_SELL = 1

# CODE_DATA market_type
KOSPI = 1
KOSDAQ = 2
