from datetime import timedelta
from Algorithm import Algorithm

class PushRightRelaxLeft(Algorithm):

    def __init__(self, input, weight, relax, name="PushRight-RelaxLeft"):
        Algorithm.__init__(self, input, weight, relax, name)
    
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        while(start <= input.schedule.dateRange.end):
            oInterval = task.interval
            start = self.shift(asset, task, start, start, oInterval, 0, input.schedule)
            # task.interval = oInterval
            
            if not task.withinInterval(input.schedule, asset, start):  
                end = input.schedule.add(asset, task, start)
                self.console(asset, task, input, start, end)
            else:
                end = start
            
            start = task.next(asset, end)
            task.interval = oInterval
            
    def bundleSchedule(self, bundle, asset, input, primary, start):
        """
        Schedule bundled tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        Check against the length of the entire bundle of tasks.
        Schedule individual tasks in consecutive order once an empty slot is found.
        """
        metatask = primary.bundleAsTask(bundle, asset)
        
        while(start <= input.schedule.dateRange.end):
            oInterval = metatask.interval
            start = self.shift(asset, metatask, start, start, oInterval, 0, input.schedule)            
            metatask.interval = oInterval
                        
            self.remainder_hours = 0            # The hours carried over from the preceding task
            self.maxhours = primary.hoursPerDay # The work hours in a day
            self.longest = 0                    # The task that takes the longest to perform
                                   
            for task in bundle:
                """For each task in the bundle, schedule in order."""
                self.overhours = False
                original = task.interval
                if(task.interval+self.relax > 0):                    
                    task.interval += self.relax
                else:
                    task.interval = 0
                if task.concurrent or not task.withinInterval(input.schedule, asset, start):
                    """Concurrent task inherits the interval of its parent task."""
                    if(task.concurrent): task.interval = primary.interval
                    """Add to schedule."""
                    end = input.schedule.add(asset, task, start)     
                    self.console(asset, task, input, start, end)
                    """Claculate the start and end dates."""
                    dates = self.calc(task, start, end)
                    start = dates[0]
                    end = dates[1]
                    if(task.concurrent and task.id in primary.concur 
                        and task.interval >= primary.interval): self.skip.add(task.id) 
                else:
                    end = start
                task.interval = original
            start = primary.next(asset, end)
            
    
    def shift(self, asset, task, start, orig, interval, n, schedule):
        while(schedule.blocked(asset, task, start)):
            if n > self.relax and start - timedelta(days=1) >= asset.start:
                """Adjust the interval so it doesn't stumble on the interval check."""
                task.interval = interval + self.relax
                start -= timedelta(days=1)
                n -= 1
                self.conflicts += 1
                # print "shove" 
            else:
                if start < orig:
                    start = orig
                task.interval = interval
                start += timedelta(days=1)
                # print "push"
                self.conflicts += 1
        return start