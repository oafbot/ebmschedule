from datetime import datetime
from datetime import timedelta
from outputs.Output import Output

class Algorithm:
    """Parent class for algorithms"""
    
    def __init__(self, input, weight, relax, name="Algorithm"):
        self.name       = name
        self.weight     = weight*0.10 # 0 <= weight <= 1
        self.totalTasks = len(input.tasks)
        self.conflicts  = 0
        self.prev       = 0
        self.output     = Output(input)
        self.stopwatch  = datetime.now()
        self.relax      = (0 - relax)*0.25
        self.skip       = set()
        self.forced     = 0
        self.metrics    = input.metrics
        self.schedule   = input.schedule
        self.stupid     = input.conf.stupid
        self.drift      = []
        self.totalScheduled = 0
        
        if(self.relax < 0):
            self.name += "["+str(abs(self.relax))+"]"
        if(input.trace): 
            self.output.console()
        if(input.conf.pushcal): 
            self.calendar(input)
        if self.name != "PushLeft":
            self.sort(input)
        self.main(input)
        
    def sort(self, input):
        """
        Prioritize the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex ( i.e. conflict heavy ) task first.
        """
        input.tasks.sort(key=lambda task: 
            (
                (self.weight * self.totalhours(task, input.tasks)) +
                ((1-self.weight) * (self.totalconflicts(task, input.tasks) / (self.totalTasks)))
                ), reverse=True
            )
            
    def main(self, input):
        for task in input.tasks:
            for asset in input.assets:
                if(task.interval):
                    """
                    If the task is to be performed at a set interval,
                    Set the new start date to the later of either:
                      A. The last time a task was performed on a given asset
                      B. The start date of the given date range.
                    """
                    start = task.next(asset, self.schedule.last(asset, task))
                    start = max(start, self.schedule.dateRange.start)
                    bundle = task.checkConstraints(list(), asset, input)
                    if len(bundle) > 1 and task.id not in self.skip:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    elif task.id not in self.skip:
                        self.regularSchedule(asset, task, input, start)
        self.analytics(input)
        self.results = input
    
    def totalhours(self, task, tasks):
        total = self.taskcost(task)
        for t in tasks:
            if t.id in task.prep:
                total += self.taskcost(t)
                total += self.totalhours(t, tasks)
            if t.id in task.prereq:
                total += self.taskcost(t)
                total += self.totalhours(t, tasks)
            if t.id in task.subseq:
                total += self.taskcost(t)
                total += self.totalhours(t, tasks)
            if t.id in task.concur:
                total += self.taskcost(t)
                total += self.totalhours(t, tasks)
        return total
    
    def totalconflicts(self, task, tasks):
        total = len(task.conflicts)
        for t in tasks:
            if t.id in task.prep:
                total += len(t.conflicts)
                total += self.totalconflicts(t, tasks)
            if t.id in task.prereq:
                total += len(t.conflicts)
                total += self.totalconflicts(t, tasks)
            if t.id in task.subseq:
                total += len(t.conflicts)
                total += self.totalconflicts(t, tasks)
            if t.id in task.concur:
                total += len(t.conflicts)
                total += self.totalconflicts(t, tasks)
        return total        
    
    def taskcost(self, task):
        """Calculate the cost ratio for skills required for a task."""
        cost = 0
        for manpower in task.manpowers:
            cost += (1.0*manpower.hours)/(manpower.skill.hoursPerDay)
        return cost
        
    def calc(self, task, start, end):
        """Find the the most costly task."""
        for manpower in task.manpowers:
            if manpower.hours > self.longest: self.longest = manpower.hours
        """If the task takes takes longer than the workday, carry over."""
        if self.longest <= self.maxhours:
            hours = self.longest
            if hours + self.remainder_hours >= self.maxhours: 
                self.overhours = True
        else: hours = self.longest % self.maxhours
        """Determine the hours remaining on a task that need to be carried over."""
        if hours + self.remainder_hours == self.maxhours:
            self.remainder_hours = 0
        elif hours + self.remainder_hours > self.maxhours:
            self.remainder_hours = (self.remainder_hours + hours) - self.maxhours
        else:
            self.remainder_hours += hours
        """Set the start date. Push to next day if overtime."""
        if self.overhours:
            start = end + timedelta(days=1)
        else: 
            start = end
        return [start, end]                
    
    def console(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""
        self.output.printSchedule(self, asset, task, start, end) 
    
    def analytics(self, input):
        """Print out the cost analysis for the algorithm."""
        now = datetime.now()
        exectime = str(now - self.stopwatch)[:-4]
        forced = "    Forced: " + str(self.forced) if self.forced else ""
        weight = str(self.weight)
        data = (self.name, self.schedule.dataSource, input.count, self.weight, self.conflicts, forced)
        output = "%s: %s %s    Weight: %s    Adjustments: %s %s" % data
        print "\n", str.ljust(output, 80), "Execution:", exectime, "\n"
        self.metrics.Forced = self.forced
        """Write out metrics to a file."""
        # if(input.conf.metrics):
        #     self.output.writeMetrics(input, self.conflicts, self.name, self.weight, exectime, now)
            
    def calendar(self, input):
        """Initiate the Google Calendar."""
        from outputs.Calendar import Calendar        
        if not self.schedule.cal: 
            self.schedule.cal = Calendar()
        self.schedule.cal.Connect(input)
    
    def usageViolation(self, date, original, schedule, asset):
        """Record usage violations."""
        if date > original and schedule.used and date not in asset.violation:
            asset.violation.update([date])
            schedule.totalUsage += 1
    
    def recordInterval(self, start, orig):
        if(start < self.schedule.dateRange.end):
            self.drift.append(start - orig)
               