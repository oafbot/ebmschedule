from datetime import timedelta
from Algorithm import Algorithm

class PushToRight(Algorithm):
    
    def __init__(self, input, weight=1.0, name="PushRight"):        
        Algorithm.__init__(self, input, weight, name)        
                       
    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        while(start <= input.schedule.dateRange.end):
            while(input.schedule.blocked(asset, task, start)):
                start += timedelta(days=1) # Shift to the right one day when blocked
                self.conflicts += 1
            if not task.withinInterval(input.schedule, asset, start):  
                end = input.schedule.add(asset, task, start) # Add to schedule
                self.console(asset, task, input, start, end)
            else : 
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
            while(input.schedule.blocked(asset, metatask, start)):
                start += timedelta(days=1)
                self.conflicts += 1
            
            remainder_hours = 0             # The hours carried over from the preceding task
            maxhours = primary.hoursPerDay  # The work hours in a day
            longest = 0                     # The task that takes the longest to perform
                        
            """For each task in the bundle, schedule in order."""
            for task in bundle:
                overhours  = False
                
                if not task.withinInterval(input.schedule, asset, start):        
                    end = input.schedule.add(asset, task, start)
                    self.console(asset, task, input, start, end)
                    
                    """Find the the most costly task."""
                    for manpower in task.manpowers:
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
                else:
                    end = start             
            start = primary.next(asset, end)
            