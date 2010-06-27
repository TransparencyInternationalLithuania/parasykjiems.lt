from datetime import datetime


class TimeMeasurer:
    def __init__(self):
        self.start = datetime.now()

    def ElapsedSeconds(self):
        now = datetime.now()
        diff = now - self.start
        return diff.seconds + diff.microseconds / 1000000.0