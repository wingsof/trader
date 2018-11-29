import numpy as np

NORMAL = 'normal'
SHORT = 'short'
MEET_DESIRED_PROFIT = 'meet_desired_profit'
BUY_WHEN_BEARISH = 'buy_when_bearish'


def right_profit(bought, low, high, close, prev_close, buy_threshold, sell_threshold, money, trade_count):
    if bought['quantity'] != 0 and low <= prev_close - sell_threshold:
        money = close * bought['quantity']
        money -= money * 0.003
        bought['quantity'] = 0
        trade_count += 1
    elif bought['quantity'] == 0 and prev_close != 0 and high >= prev_close + buy_threshold:
        bought['quantity'] = money / close
        money = 0

    return money, trade_count

def left_profit(bought, low, high, close, prev_close, buy_threshold, sell_threshold, money, trade_count):
    if bought['quantity'] is not 0 and high >= prev_close + buy_threshold:
        money = close * bought['quantity']
        money -= money * 0.003
        bought['quantity'] = 0
    elif bought['quantity'] is 0 and prev_close != 0 and low <= prev_close - sell_threshold :
        bought['quantity'] = money / close
        money = 0
        trade_count += 1

    return money, trade_count


def short_profit(bought, low, high, close, prev_close, buy_threshold, sell_threshold, money, trade_count):
    if bought['quantity'] != 0 and high >= prev_close + buy_threshold:
        money = (bought['price'] - close) * bought['quantity'] + bought['balance']
        money -= money * 0.003
        bought['quantity'] = 0
        trade_count += 1
    elif bought['quantity'] == 0 and prev_close != 0 and low <= prev_close - sell_threshold:
        bought['quantity'] = money / close
        bought['price'] = close
        bought['balance'] = money
        money = 0

    return money, trade_count

def right_sell_profit(bought, low, high, close, prev_close, buy_threshold, sell_threshold, money, trade_count):
    if bought['quantity'] != 0 and (low <= prev_close - sell_threshold or bought['price'] * 1.1 <= high):
        money = close * bought['quantity']
        money -= money * 0.003
        bought['quantity'] = 0
        trade_count += 1
    elif bought['quantity'] == 0 and prev_close != 0 and high >= prev_close + buy_threshold:
        bought['quantity'] = money / close
        bought['price'] = close
        money = 0

    return money, trade_count


def get_avg_profit_by_day_data(df, buy_t, sell_t, method):
    bought = {'quantity': 0, 'price': 0, 'balance': 0}
    prev_close = 0
    initial_deposit = 1000000
    money = initial_deposit
    trade_count = 0

    method_apply = {
        NORMAL: right_profit,
        SHORT: short_profit,
        MEET_DESIRED_PROFIT: right_sell_profit,
        BUY_WHEN_BEARISH: left_profit
    }

    for _, row in df.iterrows():
        buy_threshold = prev_close * buy_t
        sell_threshold = prev_close * sell_t

        money, trade_count = method_apply[method](bought, row['low'], row['high'],
                row['close'], prev_close, buy_threshold, sell_threshold, money, trade_count)
        prev_close = row['close']

    left = money if money != 0 else bought['quantity'] * prev_close
    return left / initial_deposit * 100, trade_count



def get_best_rate(df, method=NORMAL):
    buy_t_list = list(np.arange(0.01, 0.065, 0.001))
    sell_t_list = list(np.arange(0.01, 0.065, 0.001))
    buy_range = {}
    sell_range = {}
    for buy_t in buy_t_list:
        for sell_t in sell_t_list:
            profit, trade_count = get_avg_profit_by_day_data(df, buy_t, sell_t, method)

            if trade_count == 0: continue
            if buy_t in buy_range:
                buy_range[buy_t].extend([profit])
            else:
                buy_range[buy_t] = [profit]

            if sell_t in sell_range:
                sell_range[sell_t].extend([profit])
            else:
                sell_range[sell_t] = [profit]
    sorted_by_buy = sorted(buy_range.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=True)
    sorted_by_sell = sorted(sell_range.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=True)
    
    # when have a warning, close, high and low all values are same (no trades at all)
    if len(sorted_by_buy) == 0:
        return 0.0, 0.0, 0.0

    b_avg = sum(sorted_by_buy[0][1]) / len(sorted_by_buy[0][1])
    s_avg = sum(sorted_by_sell[0][1]) / len(sorted_by_sell[0][1])
    return sorted_by_buy[0][0], sorted_by_sell[0][0], (b_avg + s_avg) / 2



