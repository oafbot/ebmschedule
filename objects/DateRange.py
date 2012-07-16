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