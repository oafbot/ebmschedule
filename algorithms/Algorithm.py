from datetime import datetime
from datetime import timedelta
from outputs.Output import Output

class Algorithm:
    """Parent class for algorithms."""

    def __init__(self, input, weight, relax, sort="+", name="Algorithm"):
        self.name       = name
        self.weight     = weight*0.10
        self.relax      = (0 - relax)*0.25
        self.metrics    = input.metrics
        self.schedule   = input.schedule
        self.output     = Output(input)
        self.stupid     = input.conf.stupid
        self.startDate  = self.schedule.dateRange.start
        self.endDate    = self.schedule.dateRange.end
        self.conflicts  = 0
        self.prev       = 0
        self.forced     = 0
        self.drift      = []
        self.groundings = {}
        self.skip       = set()
        self.stopwatch  = datetime.now()
        self.totalTasks = len(input.tasks)
        self.totalScheduled = 0

        if(self.relax < 0):
            self.name += "["+"{0:.2f}".format(abs(self.relax))+"]"
        if(input.trace): 
            self.output.console()
        if(input.conf.pushcal): 
            self.calendar(input)
        if sort == '+':
            self.sorting = 'On'
            self.sort(input.tasks, input.assets, True)
        elif sort == '-':
            self.sorting = 'Off'
        elif sort == '!':
            self.sorting = 'Rev'
            self.sort(input.tasks, input.assets, False)
        self.main(input)

    def sort(self, tasks, assets, order):
        """
        Prioritize the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex conflict heavy task first.
        """
        bias = self.bias(tasks)
        for task in tasks:
            task.score = (self.weight * self.totalhours(task, tasks)) / bias + ((1.0-self.weight)*
                         (self.totalconflicts(task, tasks)*1.0 / self.totalTasks))
        tasks.sort(key=lambda task:task.score, reverse=order)

        for asset in assets:
            """Prioritize the assets that have usage constraints in the more imminent future."""
            for index in self.schedule.usage.dates:
                if asset.id in index:
                    d = (index.Date - (self.startDate.date()-timedelta(days=1))).days
                    asset.score += (0.9**int(d))*(1)
        assets.sort(key=lambda asset:asset.score, reverse=order)
                    
    def main(self, input):
        """Schedule tasks for each asset."""
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
                    start = max(start, self.startDate)
                    bundle = task.checkConstraints(list(), asset, input, True)
                    if len(bundle) > 1 and task.id not in self.skip:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    elif task.id not in self.skip:
                        self.regularSchedule(asset, task, input, start)
        self.analytics(input)
        self.results = input

    def bias(self, tasks):
        """Determine the natural bias found in the scoring of the tasks and normalize."""
        numerator = 0
        denominator = 0
        for task in tasks:
            numerator += self.totalhours(task, tasks)
            denominator += (self.totalconflicts(task, tasks)*1.0 / self.totalTasks)
        return numerator / denominator

    def totalhours(self, task, tasks):
        """Determine the total skill hours cost of a task and it's children."""
        total = self.taskcost(task)
        for t in tasks:
            if t.id in task.prep:
                total += self.totalhours(t, tasks)
            if t.id in task.prereq:
                total += self.totalhours(t, tasks)
            if t.id in task.subseq:
                total += self.totalhours(t, tasks)
            if t.id in task.concur:
                total += self.totalhours(t, tasks)
        return total

    def totalconflicts(self, task, tasks):
        """Determine the total conflict cost of a task and it's children."""
        total = len(task.conflicts)
        for t in tasks:
            if t.id in task.prep:
                total += self.totalconflicts(t, tasks)
            if t.id in task.prereq:
                total += self.totalconflicts(t, tasks)
            if t.id in task.subseq:
                total += self.totalconflicts(t, tasks)
            if t.id in task.concur:
                total += self.totalconflicts(t, tasks)
        return total

    def taskcost(self, task):
        """Calculate the cost ratio for skills required for a task."""
        cost = 0
        for skill in task.skills:
            cost += (1.0*skill.hours)/skill.availableHours
        # for manpower in task.manpowers:
        #     cost += (1.0*manpower.hours)/(manpower.skill.hoursPerDay*manpower.skill.available)
        return cost

    def calc(self, task, start, end):
        """Calculate the start and end dates."""
        longest = 0
        """Inherit the duration of a task from its most time-intensive procedure."""
        for manpower in task.manpowers:
            if manpower.hours > longest: longest = manpower.hours        
        hours = self.remainder + longest
                
        if hours >= self.maxhours:
            """If the tasks take longer than the workday, determine end date and remainder hours."""
            end = start + timedelta(days=int(hours / self.maxhours))
            self.remainder = hours % self.maxhours
        else:
            self.remainder = hours
        """Set start to end of the task for the next task."""
        return [end, end]

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

    def calendar(self, input):
        """Initiate the Google Calendar."""
        from outputs.Calendar import Calendar
        if not self.schedule.cal: 
            self.schedule.cal = Calendar()
        self.schedule.cal.Connect(input)

    def usageViolation(self, date, original, asset):
        """Record usage violations."""
        used_date = self.schedule.used_date
        
        if(date > original and self.schedule.used and used_date is not None):
            if(original.date() <= used_date and used_date not in asset.violation):
                asset.violation.update([used_date])
                self.schedule.totalUsage += 1
                """Keep a record of imminent usage."""
                if(date <= self.startDate + timedelta(days=90)):              
                    self.metrics.Imminent += 1
        """Reset usage flags."""
        self.schedule.used = False
        self.schedule.used_date = None
        self.schedule.used_asset = None

    def recordInterval(self, date, orig, asset):
        """Record the drift in days from the optimal scheduling day."""
        from objects.DateRange import DateRange
        
        if(date < self.endDate):
            self.drift.append(date - orig)
            # if date - orig > timedelta(days=0): print date - orig, date.date(), asset.id, task.id if task.id != 0 else task.name            
            if(date > orig):
                for ground in DateRange(orig + timedelta(days=1), date).range():
                    if((asset.id, ground.date()) not in self.groundings):
                        self.groundings.update({(asset.id, ground.date()):1})
                        # print asset.id, ground.date(), task.id if task.id != 0 else task.name
                        # self.groundings.append((asset.id, ground))
                        # self.metrics.ActualGround += 1