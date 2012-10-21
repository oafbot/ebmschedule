from datetime import timedelta
from Algorithm import Algorithm
from math import ceil
from copy import deepcopy

class PushRightRelaxLeft(Algorithm):

    def __init__(self, input, weight, relax, name="PushRight-RelaxLeft"):
        Algorithm.__init__(self, input, weight, relax, name)
    
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        original = task.interval
        while(start <= input.schedule.dateRange.end):            
            start = self.shift(asset, task, start, start, original, input.schedule)
            
            if not task.withinInterval(input.schedule, asset, start):  
                task.interval = original
                end = input.schedule.add(asset, task, start)
                self.console(asset, task, input, start, end)
            else:
                task.interval = original
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
        original = primary.interval
        
        while(start <= input.schedule.dateRange.end):
            start = self.shift(asset, metatask, start, start, original, input.schedule)           
            
            self.remainder_hours = 0            # The hours carried over from the preceding task
            self.maxhours = primary.hoursPerDay # The work hours in a day
            self.longest = 0                    # The task that takes the longest to perform
                                   
            for task in bundle:
                """For each task in the bundle, schedule in order."""
                self.overhours = False
                orig = task.interval
                
                if(task.interval + int(ceil(task.interval * self.relax)) > 0):                    
                    task.interval += int(ceil(task.interval * self.relax))
                
                if task.concurrent or not task.withinInterval(input.schedule, asset, start):
                    """Concurrent task inherits the interval of its parent task."""
                    # if(task.concurrent): 
                    #     task.interval = primary.interval
                    task.interval = orig
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
                    task.interval = orig
                    end = start
                    
            start = primary.next(asset, end)
                
    def shift(self, asset, task, start, orig, interval, schedule):
        floor = start + timedelta(days=int(ceil(interval * self.relax)))
        push  = False
        schedule.used = False
        
        while(schedule.blocked(asset, task, start)):
            if start > floor and not push and floor > asset.start:
                """Adjust the interval so it doesn't stumble on the interval check."""
                task.interval = interval + int(ceil(interval * self.relax))
                start -= timedelta(days=1)
                self.conflicts += 1
                # print "shove" 
            else:
                if start < orig:
                    start = orig
                push = True
                task.interval = interval
                start += timedelta(days=1)
                self.conflicts += 1
                # print "push" 
        self.usageViolation(start, orig, schedule, asset)
        return start