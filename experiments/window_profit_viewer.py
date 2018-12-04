import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn import preprocessing
from utils import profit_calc 
from mpl_toolkits.mplot3d import Axes3D

method = [profit_calc.NORMAL, profit_calc.SHORT, profit_calc.MEET_DESIRED_PROFIT, profit_calc.BUY_WHEN_BEARISH]


df = pd.DataFrame(columns=['date', 'profit', 'expected', 'buy_threshold', 'sell_threshold', 'price', 'method'])

if __name__ == '__main__':
    df = pd.read_excel('A005380_90.xlsx')

    normal_df = df[df['method'] == profit_calc.NORMAL]
    short_df = df[df['method'] == profit_calc.SHORT]
    meet_df = df[df['method'] == profit_calc.MEET_DESIRED_PROFIT]
    bear_df = df[df['method'] == profit_calc.BUY_WHEN_BEARISH]
    limit_df = df[df['method'] == profit_calc.LIMIT]

    dfs = [normal_df, short_df, meet_df, bear_df, limit_df]
    new_dfs = []
    for d in dfs:
        d = d.drop(['buy_threshold', 'sell_threshold', 'method'], axis=1)
        new_dfs.append(d.set_index('date'))

    normal_df = new_dfs[0]
    normal_df[['short_expected', 'short_profit']] = new_dfs[1][['expected', 'profit']]
    normal_df[['meet_expected', 'meet_profit']] = new_dfs[2][['expected', 'profit']]
    normal_df[['bear_expected', 'bear_profit']] = new_dfs[3][['expected', 'profit']]
    #normal_df[['limit_expected', 'limit_profit']] = new_dfs[4][['expected', 'profit']]

    normal_df.plot()
    plt.show()
