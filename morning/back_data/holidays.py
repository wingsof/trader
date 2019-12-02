# refer http://marketdata.krx.co.kr/mdi#document=01100305

from datetime import date, timedelta
import pandas as pd
import os

_holidays = []

def read_holiday_excel():
    global _holidays
    directory = 'morning' + os.sep + 'back_data' + os.sep + 'holiday_data'
    for subdir, _, files in os.walk(directory):
        for file in files:
            df = pd.read_excel(subdir + os.sep + file)
            for d in df.iloc[:, 0:1].iloc[:,0]:
                date_str = d.split(' ')[0].split('-')
                if len(date_str) > 0:
                    _holidays.append(date(int(date_str[0]), int(date_str[1]), int(date_str[2])))
                
read_holiday_excel()

def is_holidays(date):
    d = date if date.__class__.__name__ == 'date' else date.date()
    if d.weekday() > 4:
        return True
    else:
        if d in _holidays:
            return True
    return False


def get_working_days(from_date, until_date):
    working_days = []
    while from_date <= until_date:
        if not is_holidays(from_date):
            working_days.append(from_date)
        from_date += timedelta(days=1)
    
    return working_days