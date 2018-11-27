from datetime import datetime

class TimeManager:
    @staticmethod
    def now():
        return datetime.now()

    def __init__(self):
        pass

    def is_runnable(self, t=datetime.now()):
        if t.weekday() < 5 and t.hour >= 7 and t.hour <= 15:
            return True
        return False

    def is_order_collect_time(self, t=datetime.now()):
        print('COLLECT time check', t.hour, t.minute, flush=True)
        if t.hour == 15 and t.minute > 20 and t.minute <= 27:
            print('COLLECT OK', flush=True)
            return True
        return False

    def is_order_start_time(self, t=datetime.now()):
        if t.hour == 15 and t.minute > 27 and t.minute < 30:
            return True
        return False
    
    def is_order_wait_done_time(self, t=datetime.now()):
        if t.hour == 16 and t.minute > 30:
            return True
        return False

    def get_today(self):
        n = datetime.now()
        return datetime(n.year, n.month, n.day)

    def get_heart_beat(self):
        return 1000
