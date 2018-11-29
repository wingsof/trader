import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn import preprocessing
from mpl_toolkits.mplot3d import Axes3D

def show_by_year(df):
    df = df.drop(df['trade_count'] == 0, axis=1)


def show_by_rate(df):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.bar(df['buy_rate'], df['profit'], zs=df['sell_rate'], zdir='y', alpha=0.8)
    #df.plot(kind='scatter', x='buy_rate', y='sell_rate', s=df['trade_count'] * 10, alpha=0.4,
    #        c='profit', label='profit', cmap=plt.get_cmap('Reds'), colorbar=True)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    df = pd.read_excel('20161.xlsx')

    df = df[df['trade_count'] != 0]
    names = ['short', 'normal', 'normal_sell', 'left']

    """
    le = preprocessing.LabelEncoder()

    le.fit(names)
    df['label'] = le.transform(df['method'])
    print(df)
    show_by_rate(df[df['method'] == 'normal_sell'])
    """
    df = df[df['date'] >= datetime(2016, 1, 1)]
    print(df)
    for name in names:
        m = df.loc[df['method'] == name]['profit'].mean()
        print(name, 'mean:', '{0:0.2f}'.format(m))
"""
from mpl_toolkits.mplot3d import Axes3D

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for c, z in zip(['r', 'g', 'b', 'y'], [30, 20, 10, 0]):
    xs = np.arange(20)
    ys = np.random.rand(20)

    # You can provide either a single color or an array. To demonstrate this,
    # the first bar of each set will be colored cyan.
    cs = [c] * len(xs)
    cs[0] = 'c'
    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
    """