from datetime import timedelta
from Algorithm import Algorithm

class PushToLeft(Algorithm):
    
    def __init__(self, input, weight, name="PushLeft"):        
        Algorithm.__init__(self, input, weight, 0, name)
                       
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        loopend = False
        while(start <= input.schedule.dateRange.end):
            input.schedule.used = False
            original = start
            
            while(start > input.schedule.last(asset, task) and not loopend):
                if(input.schedule.blocked(asset, task, start, self.stupid)):
                    start -= timedelta(days=1)
                    self.conflicts += 1
                
                    if(start <= input.schedule.last(asset, task)):
                        loopend = True
                        start = original
                        self.forced += 1
                else:
                    loopend = True
            
            self.usageViolation(start, original, input.schedule, asset)
            self.recordInterval(start, original)
            
            if not task.withinInterval(input.schedule, asset, start, self.stupid):
                self.totalScheduled += 1
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
        loopend = False
        
        while(start <= input.schedule.dateRange.end):            
            input.schedule.used = False
            original = start
            
            while(start > input.schedule.last(asset, primary) and not loopend): 
                if(input.schedule.blocked(asset, metatask, start, self.stupid)):
                    start -= timedelta(days=1)
                    self.conflicts += 1
                    if(start <= input.schedule.last(asset, primary)):
                        loopend = True
                        start = original
                        self.forced += 1
                else:
                    loopend = True
            
            self.usageViolation(start, original, input.schedule, asset)
            self.recordInterval(start, original)
            
            self.remainder_hours = 0            # The hours carried over from the preceding task
            self.maxhours = primary.hoursPerDay # The work hours in a day
            self.longest = 0                    # The task that takes the longest to perform
                        
            for task in bundle:
                """For each task in the bundle, schedule in order."""
                self.overhours = False
                if task.concurrent or not task.withinInterval(input.schedule, asset, start, self.stupid):
                    self.totalScheduled += 1
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
            