from datetime import timedelta
from Algorithm import Algorithm
from math import ceil

class PushRightRelaxLeft(Algorithm):

    def __init__(self, input, weight, relax, sort='+', name="PushRight-RelaxLeft"):
        Algorithm.__init__(self, input, weight, relax, sort, name)

    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        original = task.interval
        while(start <= self.endDate):
            start = self.shift(asset, task, start, start, original)

            if not task.withinInterval(self.schedule, asset, start, self.stupid):
                task.interval = original
                self.totalScheduled += 1
                end = self.schedule.add(asset, task, start)
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

        while(start <= self.endDate):
            start = self.shift(asset, metatask, start, start, original)

            self.remainder_hours = 0            # The hours carried over from the preceding task
            self.maxhours = primary.hoursPerDay # The work hours in a day
            self.longest = 0                    # The task that takes the longest to perform

            for task in bundle:
                """For each task in the bundle, schedule in order."""
                self.overhours = False
                orig = task.interval

                if(task.interval + int(ceil(task.interval * self.relax)) > 0):
                    task.interval += int(ceil(task.interval * self.relax))

                if task.concurrent or not task.withinInterval(self.schedule, asset, start, self.stupid):
                    """Concurrent tasks always inherit the interval of its parent task."""
                    task.interval = orig
                    self.totalScheduled += 1
                    """Add to schedule."""
                    end = self.schedule.add(asset, task, start)
                    self.console(asset, task, input, start, end)
                    """Claculate the start and end dates."""
                    dates = self.calc(task, start, end)
                    start = dates[0]
                    end = dates[1]
                    if(task.concurrent and task.id in primary.concur and 
                       task.interval >= primary.interval): self.skip.add(task.id) 
                else:
                    task.interval = orig
                    end = start

            start = primary.next(asset, end)
        
    def shift(self, asset, task, start, orig, interval): 
        """If the optimal day for scheduling is blocked, try to schedule prior, if not later."""
        relax = orig + timedelta(days=int(ceil(interval * self.relax))) + timedelta(days=1) 
        last  = orig - timedelta(days=interval) + timedelta(days=1)       
        floor = relax if relax > last else last + timedelta(days=1)
        push  = False
        
        if floor < self.startDate:
            floor = self.startDate
        
        # print "relax:",relax,"last:", last
        # print "floor:",floor
        if task.id == 0:                        
            if '252205' in task.tasksInMeta():
                print "---------------------------", task.primary.id
                    
        while(self.schedule.blocked(asset, task, start, self.stupid)):
            if start > floor and not push:
                """Adjust the interval so it doesn't stumble on the interval check."""
                task.interval = interval + int(ceil(interval * self.relax))
                start -= timedelta(days=1)
                self.conflicts += 1
            else:
                if start < orig:
                    start = orig
                push = True
                task.interval = interval
                start += timedelta(days=1)
                self.conflicts += 1
                
        self.usageViolation(start, orig, asset)
        self.recordInterval(start, orig)
        return start
