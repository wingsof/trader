from datetime import datetime, timedelta

class TimeManager:
    current_dt = datetime.now()
    fake_dt = datetime(2018, 11, 1, 8, 0, 0)

    def now():
        n = datetime.now()
        time_passed = (n - TimeManager.current_dt).total_seconds()
        TimeManager.current_dt = n
        TimeManager.fake_dt += timedelta(seconds=time_passed*10)
        return TimeManager.fake_dt

    def __init__(self):
        pass

    def is_runnable(self, t=datetime.now()):
        t = TimeManager.now()
        if t.weekday() < 5 and t.hour >= 6 and t.hour <= 15:
            return True
        return False

    def is_order_collect_time(self, t=datetime.now()):
        t = TimeManager.now()
        if t.hour is 15 and t.minute > 20 and t.minute <= 27:
            return True
        return False

    def is_order_start_time(self, t=datetime.now()):
        t = TimeManager.now()
        if t.hour is 15 and t.minute > 27 and t.minute < 30:
            return True
        return False
    
    def is_order_wait_done_time(self, t=datetime.now()):
        t = TimeManager.now()
        if t.hour is 16 and t.minute > 30:
            return True
        return False

    def get_today(self):
        t = TimeManager.now()
        return datetime(t.year, t.month, t.day)

    def get_heart_beat(self):
        return 1000

