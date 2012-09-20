class DateRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def range(self):
        from datetime import timedelta
        date = self.start
        delta = timedelta(days=1)
        while date <= self.end:
            yield date
            date += delta
    
    def within(self, date):
        from datetime import timedelta
        for blocked in self.range():
            if(blocked - date > timedelta(days=0) and blocked - date < timedelta(days=1)):
                return True
        return False