class DateRange:
    def __init__(self, start, end):
        """Set start and end dates."""
        self.start = start
        self.end = end
    
    def range(self):
        """Return a range of dates."""
        from datetime import timedelta
        date = self.start
        delta = timedelta(days=1)
        while date <= self.end:
            yield date
            date += delta
    
    def within(self, date):
        """Check if the date is found in the daterange."""
        from datetime import timedelta
        if( date > self.start and date <= self.end ): 
            return True
        return False