from datetime import timedelta
import main
class PushToRight:
    
    def __init__(self, input):
        weight = 1.0 # 0 <= weight <= 1
        totalTasks = len(input.tasks)
        self.conflicts = 0
        self.prev = 0
        
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

        for asset in input.assets:
            for task in input.tasks:
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
            input.schedule.processed = []
        # input.schedule.cal.PushBatchRequest()
        self.analytics(input)

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
            end = input.schedule.add(asset, task, start) # Add to schedule
            self.output(asset, task, input, start, end)
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
                
                    self.output(asset, bundle_task, input, start, end)
                
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
                    if overhours: start = end + timedelta(days=1)
                    else: start = end
                else: end = start
                # input.schedule.processed.append(bundle_task.id)
            start = task.next(asset, end)

    def output(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""       
        main.outputs.output.printSchedule(self, asset, task, start, end) 

    def analytics(self,input):
        """Print out the cost analysis for the algorithm."""
        print "\n",                                                                            \
              "PushToRight", input.schedule.dataSource,                                        \
              "Manhours:", input.schedule.totalManhours,                                       \
              " Counts:", self.conflicts
        # main.outputs.output.writeMetrics(input, self.conflicts)



# TODO: 
# No Maintenance Period
# planned usage
# task start/end dates
# number per a year FY
# configuration
# schedule precision
# order tasks by largest size / availability

# prerequisite separate interval?