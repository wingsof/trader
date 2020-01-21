REALTIME_DATA = 0
BIDASK_DATA = 1

UNKNOWN_MARKET = -1
BEFORE_MARKET = 0
IN_MARKET = 1
AFTER_MARKET = 2


COLUMN_COUNT = 8
ASK_WEIGHT_COL = 0
ASK_TRADE_QTY_COL = 1
ASK_SPREAD_QTY_COL = 2
PRICE_COL = 3
PERCENTAGE_COL = 4
BID_SPREAD_QTY_COL = 5
BID_TRADE_QTY_COL = 6
BID_WEIGHT_COL = 7

BID_PAIR = (('4', '6'), ('8', '10'), ('12', '14'),  ('16', '18'), ('20', '22'), ('28', '30'), ('32', '34'), ('36', '38'), ('40', '42'), ('44', '46'))
ASK_PAIR = (('3', '5'), ('7', '9'), ('11', '13'), ('15', '17'), ('19', '21'), ('27', '29'), ('31', '33'), ('35', '37'), ('39', '41'), ('43', '45'))

MONGO_SERVER = 'mongodb://192.168.0.22:27017'

HIGHLIGHT_PRICE = 100000000

STATUS_NORMAL = 0
STATUS_RUNNING = 1