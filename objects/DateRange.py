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
        """Check if the date is found in the daterange."""
        if( date > self.start and date <= self.end ): 
            return True
        return False