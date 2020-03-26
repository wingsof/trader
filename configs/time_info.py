# -- 5 - VBOX TURN OFF - 6:30 ---
# ------------------------------- 7 - SUBSCRIBER START ---------- 18:30 -- VALIDATE START -----------
# Turn off server when VBOX is turned off and restart after 10 minutes

TIME_DELTA = 0

VBOX_CHECK_INTERVAL = 60 # 1 minute

SUBSCRIBER_START_TIME = {'hour': 7, 'minute': 25}
SUBSCRIBER_FINISH_TIME = {'hour': 18, 'minute': 30}

VBOX_TURN_OFF_FROM_TIME = {'hour': 5, 'minute': 0}
VBOX_TURN_OFF_UNTIL_TIME = {'hour': 7, 'minute': 0}

MARKET_OPEN_TIME = {'hour': 9+TIME_DELTA, 'minute': 0}
MARKET_CLOSE_TIME = {'hour': 15+TIME_DELTA, 'minute': 20}
