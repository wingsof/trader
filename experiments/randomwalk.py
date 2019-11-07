import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import time_converter
from dbapi import stock_chart
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class RandomWalk:
    SIMULATION_COUNT = 10

    def __init__(self, data):
        # Collect data and divide into 2 group, first 90 days data for mu and sigma and last days for checking speculation 
        df = pd.DataFrame(list(map(lambda x: {'date': time_converter.intdate_to_datetime(x['0']), 'close': x['5']}, data)))

        if len(df) < 100:
            print('Data is less than 100 days')
            sys.exit(1)
        df = df.set_index('date')

        self.calculating = df[:90]
        self.simulation = {}
        self.simulation['Actual'] = list(df.close.iloc[90:].values)
        for i in range(RandomWalk.SIMULATION_COUNT):
            self.simulation['Simulation' + str(i)] = [df.close.iloc[90]]

    def generate_signals(self):
        mu = self.calculating.close.pct_change().mean()
        sigma = self.calculating.close.pct_change().std()

        for s in range(RandomWalk.SIMULATION_COUNT):
            for i in range(len(self.simulation['Actual']) - 1):
                next_day = self.simulation['Simulation' + str(s)][-1] * np.exp((mu - (sigma ** 2 / 2)) + sigma * np.random.normal())
                self.simulation['Simulation' + str(s)].append(next_day)
        return self.simulation


if __name__ == '__main__':
    _, data = stock_chart.get_day_period_data('A005380', datetime(2019, 1, 1), datetime.now())
    mac = RandomWalk(data)
    simulation_df = pd.DataFrame(mac.generate_signals())


    fig = plt.figure()
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(111, ylabel='price')
    _ = simulation_df.plot(ax=ax1)
    #simulation_df[['Actual', 'Simulation']].plot(ax=ax1, lw=1.)

    plt.show()
