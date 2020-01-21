from datetime import datetime

class TimeManager:
    @staticmethod
    def now():
        return datetime.now()

    def __init__(self):
        pass

    def is_runnable(self, t=datetime.now()):
        n = datetime.now()
        if n.weekday() < 5 and n.hour >= 7 and n.hour <= 15:
            return True
        return False

    def is_order_collect_time(self, t=datetime.now()):
        n = datetime.now()
        if n.hour == 15 and n.minute > 20 and n.minute <= 27:
            return True
        return False

    def is_order_start_time(self, t=datetime.now()):
        n = datetime.now()
        if n.hour == 15 and n.minute > 27 and n.minute < 30:
            return True
        return False
    
    def is_order_wait_done_time(self, t=datetime.now()):
        n = datetime.now()
        if n.hour == 16 and n.minute > 30:
            return True
        return False

    def get_today(self):
        n = datetime.now()
        return datetime(n.year, n.month, n.day)

    def get_heart_beat(self):
        return 1000
