from datetime import datetime


class TimeMeasurer:
    """ Helps measure time needed to perform a function.
    If there is already another Py package that does this, and does better,
    remove this class by marking it deprecated"""
    def __init__(self):
        self.start = datetime.now()

    def ElapsedSeconds(self):
        """Returns number of elapsed seconds with miliseconds from the time this object
         has been created"""
        now = datetime.now()
        diff = now - self.start
        return diff.seconds + diff.microseconds / 1000000.0