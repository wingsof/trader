import pandas as pd
import os
import sys


if __name__ == '__main__':
    sheet_names = ['2-3', '2-4', '2-5', '2-6', '2-26', '2-27']
    for sn in sheet_names:
        trading_dict = dict()
        total_tax = 0
        total_buy = 0
        total_sell = 0
        df = pd.read_excel(
                os.environ['MORNING_PATH'] + os.sep +
                'sample_data' + os.sep + 'bjj_trading.xlsx',
                sheet_name=sn,
                header=None)
        # trading_dict = key: code_name, stock: [], profit
        for index, row in df.iterrows():
            # 0: date, 1: buy/sell 2: name 3: price 4: quantity 5 : amount
            name = row[2]
            ttype = 1 if row[1] == '매수' else 0
            price = row[3]
            qty = row[4]
            if name not in trading_dict:
                if ttype == 1:
                    trading_dict[name] = {'stock': [{'price': price, 'qty': qty}], 'profit': 0}
                    total_buy += price * qty
                else:
                    print('Error')
                    sys.exit(1)
            elif name in trading_dict:
                if ttype == 1:
                    trading_dict[name]['stock'].append({'price': price, 'qty': qty})
                    total_buy += price * qty
                else: #ttype == 2
                    for td in trading_dict[name]['stock']:
                        if td['qty'] - qty >= 0:
                            td['qty'] -= qty
                            profit = (price - td['price']) * qty
                            tax = price * qty * 0.0025
                            total_sell += price * qty
                            total_tax += tax
                            profit -= tax
                            trading_dict[name]['profit'] += profit
                        else:
                            qty -= td['qty']
                            sold_qty = td['qty']
                            td['qty'] = 0
                            profit = (price - td['price']) * sold_qty
                            total_sell += price * sold_qty
                            tax = price * sold_qty * 0.0025
                            total_tax += tax
                            profit -= tax
                            trading_dict[name]['profit'] += profit

        print(sn, 'Profit', sum([td['profit'] for k, td in trading_dict.items()]))
        print(sn, 'tax', total_tax, 'pure profit', (total_sell - total_buy) / total_buy * 100, 'total buy', total_buy)
