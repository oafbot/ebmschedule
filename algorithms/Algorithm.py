from datetime import datetime
from datetime import timedelta
from outputs.Output import Output

class Algorithm:
    """Parent class for algorithms."""

    def __init__(self, input, weight, relax, sort="+", name="Algorithm"):
        self.name       = name
        self.weight     = weight*0.10       # The weight given to each side of the sort
        self.relax      = (0 - relax)*0.25  # The amount an algorithm is permitted to relax left
        self.metrics    = input.metrics
        self.schedule   = input.schedule
        self.output     = Output(input)
        self.stupid     = input.conf.stupid # Stupidity compensation: implementation off
        self.prev       = 0                 # Previous asset id. Used for output formatting.
        self.adjust     = 0                 # A count for adjustments made
        self.forced     = 0                 # A count of forced schedulings: implementation off
        self.drift      = []                # Drift in days from optimal scheduling
        self.groundings = {}                # The count of days an asset is grounded
        self.skip       = set()             # Tasks to be skipped in the scheduling
        self.totalTasks = len(input.tasks)
        self.totalSched = 0
        self.startDate  = self.schedule.dateRange.start
        self.endDate    = self.schedule.dateRange.end
        self.stopwatch  = datetime.now()

        """Set the name of the algorithm."""
        if(self.relax < 0): self.name += "["+"{0:.2f}".format(abs(self.relax))+"]"
        """Output scheduling to screen if trace is on.""" 
        if(input.trace): self.output.console()
        """Push schedule to Google Calendar if true."""
        if(input.conf.pushcal): self.calendar(input)
        """Run sorting algorithms. Bypass for sorting off."""
        if sort == '+':
            self.sorting = 'On'
            self.sort(input.tasks, input.assets, True)
        elif sort == '-':
            self.sorting = 'Off'
        elif sort == '!':
            self.sorting = 'Rev'
            self.sort(input.tasks, input.assets, False)
        """Run main scheduling algorithm."""
        self.main(input)

    def sort(self, tasks, assets, order):
        """
        Sort tasks according to resource cost vs. conflict cost. 
        Sort assets according to usage requirements.
        """
        bias = 1.0
        # bias = self.bias(tasks) # Compensate for natural bias in numbers
        for task in tasks:
            """Prioritize tasks that require higher percentage of resources vs. conflict heavy ones."""
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
                    """Check constraints and create a bundle of tasks."""
                    bundle = task.checkConstraints(list(), asset, input, True)
                    """Schedule as a multi-task bundle else as single tasks."""
                    if len(bundle) > 1 and task.id not in self.skip:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    elif task.id not in self.skip:
                        self.regularSchedule(asset, task, input, start)
        self.analytics(input)
        """Save scheduling results."""
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
        """Determine the total skill hours cost of a task and it's children recursively."""
        total = self.taskcost(task)
        for t in tasks:
            """Recursively derive a summation of skill-availability quotient."""
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
        """Determine the total conflict cost of a task and it's children recursively."""
        total = len(task.conflicts)
        for t in tasks:
            """Recursively count all conflicts."""
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
        """Calculate the cost ratio for skills required for a task by determining 
        how much of the skill hours for the task are available."""
        cost = 0
        for skill in task.skills:
            """Divide manhours with total available manhours."""
            cost += (1.0*skill.hours)/skill.availableHours
            # cost += (skill.availableHours - 1.0*skill.hours)/skill.availableHours
        return cost

    def calc(self, task, start, end):
        """Calculate the start and end dates of a task in a bundle."""
        longest = 0
        """Inherit the duration of a task from its most time-intensive procedure."""
        for manpower in task.manpowers:
            if manpower.hours > longest: longest = manpower.hours
        hours = round(self.remainder + longest, 2)

        if hours >= self.maxhours:
            """If the tasks take longer than the workday, determine end date and remainder hours."""
            end = start + timedelta(days=int(hours / self.maxhours))
            self.remainder = hours % self.maxhours
        else:
            self.remainder = hours
        """Set start to end of the task for the next task."""
        return [end, end]

    def usageViolation(self, date, original, asset):
        """Record usage violations."""        
        if(date > original and self.schedule.used):
            for used_date in self.schedule.used:
                if(original.date() <= used_date and used_date not in asset.violation):
                    """If the date occurs later than optimal date, and usage date is not already counted."""
                    asset.violation.update([used_date])
                    self.schedule.usageViolation += 1
                    """Keep a record of imminent usage violations."""
                    if(used_date <= self.startDate.date() + timedelta(days=14)):              
                        self.metrics.Imminent += 1
                    """Keep a record of midterm usage violations."""
                    if(used_date <= self.startDate.date() + timedelta(days=90)):              
                        self.metrics.Midterm += 1
        """Reset usage flags."""
        self.schedule.unsetUsage()

    def recordInterval(self, date, orig, asset):
        """Record the drift in days from the optimal scheduling day."""
        from objects.DateRange import DateRange
        
        if(date < self.endDate):
            """Record the dift in days from optimal scheduling day."""
            self.drift.append(date - orig)
            """For schedulings that resulted in groundings capture addtional metrics."""
            if(date > orig):
                if(asset.id, date) not in self.groundings:
                    """Capture every distinct grouning event."""
                    self.metrics.Groundings += 1
                for ground in DateRange(orig + timedelta(days=1), date).range():
                    """Capture distinct days assets are grounded."""
                    if((asset.id, ground) not in self.groundings):
                        self.groundings[(asset.id, ground)] = 1

    def console(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""
        self.output.printSchedule(self, asset, task, start, end) 

    def analytics(self, input):
        """Print out the cost analysis for the algorithm."""
        now = datetime.now()
        exectime = str(now - self.stopwatch)[:-4]
        self.output.analytics(self, exectime, input.count)
        self.metrics.Forced = self.forced

    def calendar(self, input):
        """Initiate the Google Calendar."""
        from outputs.Calendar import Calendar
        if not self.schedule.cal: 
            self.schedule.cal = Calendar()
        self.schedule.cal.Connect(input)
