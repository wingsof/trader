import numpy as np


divider = 10

def get_invest3(all_asset):
    minimum_price = 10000
    invest = all_asset
    if all_asset < minimum_price:
        invest = 0
    else:
        invest = int(invest / minimum_price) * minimum_price

    all_asset -= invest
    return all_asset, invest


def get_invest2(all_asset):
    minimum_price = 10000
    fixed_amount = 1000000
    invest = fixed_amount
    if all_asset < fixed_amount:
        invest = 0
    else:
        invest = int(invest / minimum_price) * minimum_price

    all_asset -= invest
    return all_asset, invest

def get_invest1(all_asset):
    minimum_price = 10000

    invest = all_asset / divider

    if invest / minimum_price < 1:
        invest = 0
    else:
        invest = int(invest / minimum_price) * minimum_price

    all_asset -= invest
    return all_asset, invest


#def get_invest(all_asset):
#    return get_invest3(all_asset)


def trading(all_asset):
    count_per_day = np.random.normal(4.7, 4.8, 205)
    profit_per_trade = np.random.normal(0.0201, 0.0885, 964)

    average_holding = np.random.normal(25, 33, 964)
    #all_asset = 10000000
    average_holding = list(average_holding)
    profit_per_trade = list(profit_per_trade)
    count_per_day = list(count_per_day)
    count_per_day.extend([0] * 100)

    trades = []
    results = []
    trade_count = 0
        

    for day, i in enumerate(count_per_day):
        today_count = int(i)
        if today_count < 0:
            today_count = 0

        prev_trade = len(trades)
        for _ in range(today_count):
            if len(profit_per_trade) == 0:
                break
            
            profit = profit_per_trade.pop()
            holding_days = int(average_holding.pop())

            if holding_days + day >= len(count_per_day):
                holding_days = len(count_per_day) - day - 1
            elif holding_days < 1 :
                holding_days = 1

            holding_days += day
            all_asset, invest = get_invest(all_asset)
            if invest == 0:
                break

            #print('INV', invest, invest + invest * (profit - 0.0025))
            trades.append((holding_days, invest + invest * (profit - 0.0025)))
        #print(day, 'TODAY BUY', len(trades) - prev_trade, all_asset)
        prev_trade = len(trades)
        i = 0
        while i < len(trades):
            if trades[i][0] == day:
                all_asset += trades[i][1]
                trades.remove(trades[i])
                trade_count += 1
                i -= 1
            i += 1
         
        #print(day, 'TODAY SELL', prev_trade - len(trades), all_asset)

    #print('LEFT', len(trades), 'ASSET', all_asset)
    return all_asset, trade_count

method = [get_invest1, get_invest2, get_invest3]

get_invest = get_invest1

for i in range(3):
    return_average = []
    get_invest = method[i]
    count_average = []
    for _ in range(1000):
        all_asset = 10000000
        for i in range(5):
            all_asset, count = trading(all_asset)
            count_average.append(count)
        return_average.append(all_asset)

    print(i, 'ASSET', np.array(return_average).mean(), 'COUNT', np.array(count_average).mean())

