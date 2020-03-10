
BUY_FAIL                    = 0
BUY_WAIT                    = 1
BUY_ORDER_SEND_DONE         = 2
BUY_ORDER_CONFIRM           = 3
BUY_SOME                    = 4
BUY_CANCEL                  = 5
BUY_DONE                    = 6
SELL_FAIL                   = 7
SELL_WAIT                   = 8     # for SellStage
SELL_PROGRESSING            = 9     # for SellStage
SELL_ORDER_IN_TRANSACTION   = 10    # for items
SELL_ORDER_READY            = 11    # for items
SELL_DONE                   = 13    # for SellStage/items


def status_to_str(status):
    if status == BUY_FAIL:
        return 'BUY_FAIL'
    elif status == BUY_WAIT:
        return 'BUY_WAIT'
    elif status == BUY_ORDER_SEND_DONE:
        return 'BUY_ORDER_SEND_DONE'
    elif status == BUY_ORDER_CONFIRM:
        return 'BUY_ORDER_CONFIRM'
    elif status == BUY_SOME:
        return 'BUY_SONE'
    elif status == BUY_CANCEL:
        return 'BUY_CANCEL'
    elif status == BUY_DONE:
        return 'BUY_DONE'
    elif status == SELL_FAIL:
        return 'SELL_FAIL'
    elif status == SELL_WAIT:
        return 'SELL_WAIT'
    elif status == SELL_PROGRESSING:
        return 'SELL_PROGRESSING'
    elif status == SELL_ORDER_IN_TRANSACTION:
        return 'SELL_ORDER_IN_TRANSACTION'
    elif status == SELL_ORDER_READY:
        return 'SELL_ORDER_READY'
    elif status == SELL_DONE:
        return 'SELL_DONE'

    return 'UNKNOWN'
