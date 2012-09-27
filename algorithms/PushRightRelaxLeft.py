from datetime import timedelta
from Algorithm import Algorithm

class PushRightRelaxLeft(Algorithm):

    def __init__(self, input, weight=1.0, name="PushRight-RelaxLeft"):
        Algorithm.__init__(self, input, weight, name, -3)
    
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        while(start <= input.schedule.dateRange.end):
            oInterval = task.interval
            start = self.shift(asset, task, start, start, oInterval, 0, input.schedule)
            task.interval = oInterval
            
            if not task.withinInterval(input.schedule, asset, start):  
                end = input.schedule.add(asset, task, start)
                self.console(asset, task, input, start, end)
            else :
                end = start
            start = task.next(asset, end)

            
    def bundleSchedule(self, bundle, asset, input, task, start):
        """
        Schedule bundled tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        Check against the length of the entire bundle of tasks.
        Schedule individual tasks in consecutive order once an empty slot is found.
        """
        metatask = task.bundleAsTask(bundle, asset)
        proc = set()
        skip = []
        
        for i in self.processed:
            for concur in task.concur:
                if concur in self.processed[i]:
                    skip.append(concur) # pass
                    # return
        
        while(start <= input.schedule.dateRange.end):
            oInterval = metatask.interval
            start = self.shift(asset, metatask, start, start, oInterval, 0, input.schedule)            
            metatask.interval = oInterval
            
            remainder_hours = 0            # The hours carried over from the preceding task
            maxhours = task.hoursPerDay    # The work hours in a day
            longest = 0                    # The task that takes the longest to perform
                       
            """For each task in the bundle, schedule in order."""
            for bundle_task in bundle:
                overhours  = False
                if not bundle_task.withinInterval(input.schedule, asset, start):
                    end = input.schedule.add(asset, bundle_task, start)     
                    self.console(asset, bundle_task, input, start, end)
                
                    """Find the the most costly task."""
                    for manpower in bundle_task.manpowers:
                        if manpower.hours > longest: longest = manpower.hours
                
                    """If the task takes takes longer than the workday, carry over."""
                    if longest <= maxhours:
                        hours = longest
                        if hours + remainder_hours >= maxhours: overhours = True
                    else: hours = longest % maxhours
                
                    """Determine the hours remaining on a task that need to be carried over."""
                    if hours + remainder_hours == maxhours:
                        remainder_hours = 0
                    elif hours + remainder_hours > maxhours:
                        remainder_hours = (remainder_hours + hours) - maxhours
                    else:
                        remainder_hours += hours
                
                    """Set the start date. Push to next day if overtime."""
                    if overhours: 
                        start = end + timedelta(days=1)
                    else: 
                        start = end
                    if(bundle_task.concurrent and bundle_task.id in task.concur):
                       proc.add(task.id) 
                else: 
                    end = start
            if(proc):
                self.processed[asset.id].update(proc)
            start = task.next(asset, end)
    
    def shift(self, asset, task, start, orig, interval, n, schedule):
        while(schedule.blocked(asset, task, start)):
            if n > self.relax and start - timedelta(days=1) >= asset.start:
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