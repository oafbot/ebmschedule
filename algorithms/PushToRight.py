from datetime import timedelta
from Algorithm import Algorithm

class PushToRight(Algorithm):
    
    def __init__(self, input, weight, name="PushRight"):        
        Algorithm.__init__(self, input, weight, 0, name)
                       
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        while(start <= input.schedule.dateRange.end):
            input.schedule.used = False
            origin = start
                        
            while(input.schedule.blocked(asset, task, start)):
                """Shift to the right one day when blocked."""
                start += timedelta(days=1)
                self.conflicts += 1
            
            self.usageViolation(start, origin, input.schedule, asset)
            
            if not task.withinInterval(input.schedule, asset, start): 
                """Add to schedule."""
                end = input.schedule.add(asset, task, start)
                self.console(asset, task, input, start, end)
            else:
                end = start
            start = task.next(asset, end)
    
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
            input.schedule.used = False
            origin = start
                        
            while(input.schedule.blocked(asset, metatask, start)):
                """Shift to the right one day when blocked."""
                start += timedelta(days=1)
                self.conflicts += 1
            
            self.usageViolation(start, origin, input.schedule, asset)
                        
            self.remainder_hours = 0             # The hours carried over from the preceding task
            self.maxhours = primary.hoursPerDay  # The work hours in a day
            self.longest = 0                     # The task that takes the longest to perform
                                    
            for task in bundle:
                """For each task in the bundle, schedule in order."""
                self.overhours  = False
                if task.concurrent or not task.withinInterval(input.schedule, asset, start):        
                    """Concurrent task inherits the interval of its parent task."""
                    if task.concurrent: task.interval = primary.interval                        
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
            start = primary.next(asset, end)
              