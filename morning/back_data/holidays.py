# refer http://marketdata.krx.co.kr/mdi#document=01100305

from datetime import date, timedelta
import pandas as pd
import os

_holidays = []

def read_holiday_excel(directory='morning' + os.sep + 'back_data' + os.sep + 'holiday_data'):
    global _holidays

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

def get_yesterday(today):
    today = today if today.__class__.__name__ == 'date' else today.date()

    yesterday = today - timedelta(days=1)
    while is_holidays(yesterday):
        yesterday -= timedelta(days=1)

    return yesterday


def get_date_by_previous_working_day_count(today, count):
    until_d = today
    current_d = today
    while count > 0:
        current_d = get_yesterday(current_d)
        count -= 1                
    return current_d


def count_of_working_days(from_date, until_date):
    from_d = from_date
    until_d = until_date
    count_of_days = 0
    while from_d <= until_d:
        if is_holidays(from_d):
            from_d += timedelta(days=1)
            continue
        count_of_days += 1
        from_d += timedelta(days=1)
    return count_of_days


def get_tomorrow(today):
    today = today if today.__class__.__name__ == 'date' else today.date()
    tomorrow = today + timedelta(days=1)
    while is_holidays(tomorrow):
        tomorrow += timedelta(days=1)

    return tomorrow


def get_working_days(from_date, until_date):
    from_date = from_date if from_date.__class__.__name__ == 'date' else from_date.date()
    until_date = until_date if until_date.__class__.__name__ == 'date' else until_date.date()
    
    working_days = []
    while from_date <= until_date:
        if not is_holidays(from_date):
            working_days.append(from_date)
        from_date += timedelta(days=1)
    
    return working_days
