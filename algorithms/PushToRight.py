from datetime import datetime
from datetime import timedelta
from outputs.Output import Output

class PushToRight:
    
    def __init__(self, input):
        weight = 1.0 # 0 <= weight <= 1
        totalTasks = len(input.tasks)
        self.conflicts = 0
        self.prev = 0
        self.name = "PushRight"        
        self.output = Output(input)
        self.stopwatch = datetime.now()
        
        if(input.trace): 
            self.output.console()
        if(input.conf.pushcal): 
            self.calendar(input)
        
        """
        Prioritize the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex ( i.e. conflict heavy ) task first.
        """
        input.tasks.sort(key=lambda task: 
            (     
                (weight * ((task.manhours / (task.totalAvailableHours *1.0)) 
                if task.totalAvailableHours else 0)) + 
                ((1-weight) * (len(task.conflicts) / (totalTasks *1.0)))
            ),
            reverse=True)
        
        
        for task in input.tasks:
            for asset in input.assets:
                if(task.interval):
                    """
                    If the task is to be performed at a set interval,
                    Set the new start date to the later of either:
                      A. The last time a task was performed on a given asset
                      B. The start date of the given date range.
                    """ 
                    start = task.next(asset, input.schedule.last(asset, task))
                    start = max(start, input.schedule.dateRange.start)
                    bundle = task.checkConstraints(list(), asset, input)
                    if len(bundle) > 1:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    else:
                        self.regularSchedule(asset, task, input, start)
                input.schedule.processed.clear()
        self.analytics(input)
        self.results = input
        
       
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
                # print "push"
            end = input.schedule.add(asset, task, start) # Add to schedule
            self.console(asset, task, input, start, end)
            start = task.next(asset, end)
        return start
    
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
        while(start <= input.schedule.dateRange.end):
            while(input.schedule.blocked(asset, metatask, start)):
                start += timedelta(days=1)
                self.conflicts += 1
                # print "push"
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
                        proc.add(bundle_task.id)
                else:
                    end = start
            input.schedule.processed.update(proc)
            start = task.next(asset, end)
    
    def console(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""
        self.output.printSchedule(self, asset, task, start, end) 
    
    def analytics(self,input):
        """Print out the cost analysis for the algorithm."""
        print "\n", \
              self.name + ":", input.schedule.dataSource, input.count, \
              "    Manhours:", input.schedule.totalManhours, \
              "    Adjustments:", self.conflicts
        print "\nExecution:", str(datetime.now()-self.stopwatch)[:-4]
        
        """Write out metrics to a file."""
        if(input.conf.metrics):
            self.output.writeMetrics(input, self.conflicts)
    
    def calendar(self,input):
        """Initiate the Google Calendar."""
        from outputs.Calendar import Calendar
        
        if not input.schedule.cal: 
            input.schedule.cal = Calendar()
        
        input.schedule.cal.Connect(input)