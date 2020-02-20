# Server Info
CLIENT_SOCKET_PORT = 43100
CLIENT_WEB_PORT = 5000
SERVER_IP = '192.168.0.22'


# Vendor
CYBOS = 'cybos'
KIWOOM = 'kiwoom'

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
SHUTDOWN = 'shutdown'

SUBSCRIBE_STATS = 'subscribe_stats'
COLLECTOR_STATS = 'collector_stats'


DAY_DATA = 'day_data'
TODAY_MINUTE_DATA = 'today_min_data'
TODAY_TICK_DATA = 'today_tick_data'
MINUTE_DATA = 'minute_data'
ABROAD_DATA = 'abroad_data'
CODE_DATA = 'code_data'
USCODE_DATA = 'uscode_data'
INVESTOR_DATA = 'investor_data'
INVESTOR_ACCUMULATE_DATA = 'investor_accumulate_data'

GET_LONG_LIST = 'long_list'
ORDER_STOCK = 'order_stock'
MODIFY_ORDER = 'modify_order'
CANCEL_ORDER = 'cancel_order'
ORDER_IN_QUEUE = 'order_queue'
BALANCE = 'balance'

STOCK_DATA = 'stock_realtime'
BIDASK_DATA = 'bidask_realtime'
WORLD_DATA = 'world_realtime'
INDEX_DATA = 'index_realtime'
ALARM_DATA = 'alarm_realtime'
SUBJECT_DATA = 'subject_realtim'

STOP_STOCK_DATA = 'stock_stop_realtime'
STOP_BIDASK_DATA = 'bidask_stop_realtime'
STOP_WORLD_DATA = 'world_stop_realtime'
STOP_INDEX_DATA = 'index_stop_realtime'
STOP_ALARM_DATA = 'stop_alarm_realtime'
STOP_SUBJECT_DATA = 'subject_stop_realtime'

BACK_DATA = 'stock_backdata'
COLLECTOR_DATA = 'collector_data'
TRADE_DATA = 'trade_realtime'
STOP_TRADE_DATA = 'trade_stop_realtime'

# codes
STOCK_ALARM_CODE = 'STOCK_ALARM'

# Suffix for subscribe
BIDASK_SUFFIX = '_BA'
SUBJECT_SUFFIX = '_S'
WORLD_SUFFIX = '_W'
INDEX_SUFFIX = '_I'

# Period Type for abroad
PERIOD_DAY = 'D'
PERIOD_WEEK = 'W'
PERIOD_MONTH = 'M'

# Capability
CAPABILITY_REQUEST_RESPONSE=1
CAPABILITY_COLLECT_SUBSCRIBE=2
CAPABILITY_TRADE=4


ORDER_BUY = 2
ORDER_SELL = 1

# CODE_DATA market_type
KOSPI = 1
KOSDAQ = 2

# US Code Type
USTYPE_ALL=1
USTYPE_COUNTY=2
USTYPE_UPJONG=3
USTYPE_JONGMOK=4
USTYPE_DR=5
USTYPE_RAW=6
USTYPE_EXCHANGE=7
