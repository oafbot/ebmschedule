from datetime import timedelta
from math import ceil
class Task:

    def __init__(self, id, name, workhours, threshold, interval, manpowers, 
                 conflicts=list(), prep=list(), prereq=list(), subseq=list(), concur=list()):

        self.id                  = id
        self.name                = name
        self.threshold           = threshold
        self.interval            = interval
        self.manpowers           = manpowers
        self.conflicts           = set(conflicts)
        self.prep                = set(prep)
        self.prereq              = set(prereq)
        self.subseq              = set(subseq)
        self.concur              = set(concur)
        self.locked              = False
        self.hoursPerDay         = workhours
        self.skills              = []
        self.days                = 0
        self.manhours            = 0
        self.totalAvailableHours = 0
        self.child               = False
        self.required            = False
        self.preparatory         = False
        self.concurrent          = False
        self.primary             = False
        self.subsequent          = False
        self.relax               = timedelta(days=int(ceil(self.interval/4)))
        # self.relax               = timedelta(days=1)
        self.requisite_interval  = int(ceil(self.interval/2))

        if len(manpowers): self.precal() #TODO: Should come from sequencing


    def next(self, asset, date):
        """
        If date is not set, return the start date plus the number of days 
        stipulated by the threshold.
        Otherwise return the latter of:
         A. date plus the delta of interval
         B. start date plus the delta of threshold
        """
        if date == None: 
            return self.addDays(asset.start, self.threshold)
        return self.addDays(date, self.interval)

    def end(self, start):
        """Calculate end date based on start date plus number of days task takes."""
        return self.addDays(start, self.days)

    def dateRange(self, date):
        """Set the date range"""
        from objects.DateRange import DateRange
        self._start = date
        self._end = self.end(date)
        self.dateRange = DateRange(date, self.end(date))

    def addDays(self, date, days):
        """Return the sum of the date and the time difference between today and 'days'-1."""
        from datetime import timedelta
        from math import floor
        if days > 0:
            days -= 1
        return date + timedelta(days=floor(days)) #todo: decrement precision if decimal

    def precal(self):
        """Round to the next interger day for required skill."""
        from math import ceil
        for manpower in self.manpowers:
            #TODO: Don't hard-code
            self.days = int(max(self.days, ceil(manpower.hours / manpower.skill.hoursPerDay))) 
            self.sumSkills(manpower)
            self.manhours += manpower.hours

    def sumSkills(self, manpower):
        """If the skill is in the list of required skills add manpower hours."""
        newSkill = manpower.skill.copy()
        for _skill in self.skills:
            if newSkill.id == _skill.id:
                _skill.hours += manpower.hours
                return
        newSkill.hours = manpower.hours
        self.skills.append(newSkill)

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    def schedule(self, date):
        _task = self.copy()
        _task.dateRange(date) #Calculate/set date range
        return _task

    def forceSchedule(self, dateRange):
        _task = self.copy()
        _task.dateRange = dateRange
        _task.locked = True
        return _task

    def checkConstraints(self, bundle, asset, input, prime=False):
        """Check the constrains and bundle tasks together when appropriate."""
        if self.prereq: bundle = self.satisfyRequisite(bundle, asset, input)
        """Prerequisite task."""
        if self.prep: bundle = self.bundle(bundle, self.prep, asset, input, type="prep")
        """Preparatorytask."""
        if not bundle or self not in bundle: 
            """Primary task."""
            self.primary = True if prime else False
            bundle.append(self)
        if self.concur: bundle = self.concurrence(bundle, asset, input)
        """Concurrent task."""
        if self.subseq: bundle = self.bundle(bundle, self.subseq, asset, input, type="subseq")
        """Subsequent task."""
        return bundle

    def satisfyRequisite(self, bundle, asset, input):
        """Find out if a prerequisite has been satisfied. If not schedule the prerequisite."""
        from datetime import timedelta
        requirelist = []
        """Find the task associated with the requisite id."""
        for t in input.tasks:
            for r in self.prereq:
                if t.id == r:
                    t.required = True
                    requirelist.append(t)
        """For the requirement, find out if it has been performed within the interval."""
        for require in requirelist:
            for t in input.tasks:
                if require.id == t.id:
                    if(not self.requisiteSatisfied(input, asset, t)):
                        bundle = self.bundle(bundle, self.prereq, asset, input)
        return bundle

    def requisiteSatisfied(self, input, asset, task, date=None):
        if(date==None):
            date = input.schedule.dateRange.start
        last = input.schedule.last(asset, task)
        start = self.next(asset, input.schedule.last(asset, self))
        start = max(start, date)
        if(last is None):
            return False
        elif(last < start - timedelta(days=self.requisite_interval)):
            return False
        return True

    def concurrence(self, bundle, asset, input):
        """Negotiate the appropriate scheduling for concurrent tasks."""
        concurlist = []
        tasks_set  = False

        for t in input.tasks:
            for c in self.concur:
                if t.id == c:
                    t.concurrent = True
                    concurlist.append(t)
        
        for concurrent in concurlist:
            """Check if tasks are already in the Bundle."""
            tasks_set = True if concurrent in bundle else False
        
        for concurrent in concurlist:
            """If all tasks are in the bundle return the bundle."""
            if tasks_set and self in bundle:
                return bundle
            bundle = self.bundle(bundle, self.concur, asset, input)
        return bundle

    def bundle(self, bundle, tasks, asset, input, type=None):
        """Bundle related tasks together."""
        for t in tasks:
            for task in input.tasks:
                if task.id == t:
                    task.child = True
                    task.primary = False
                    task.subsequent = True if type == "subseq" else False 
                    task.preparatory = True if type == "prep"  else False
                    bundle = task.checkConstraints(bundle, asset, input)
                    # if bundle and task not in bundle: return bundle.append(task)
        return bundle

    def unbundle(self, bundle):
        bundle = bundle.reverse().remove(self)
        return bundle.reverse()

    def bundleAsTask(self, bundle, asset):
        """Convert a bundle into a meta-task for running schedule calculations."""
        from Bundle import Bundle
        # mp = []
        # cf = set()
        # name = ""
        # threshold = 0
        # interval  = 0
        # 
        # for task in bundle:
        #     mp.extend(task.manpowers)
        #     cf.union(task.conflicts)
        #     name += str(task.id) + "-"
        #                 
        #     if task.primary:
        #         prime = task
        #         interval = task.interval
        #         threshold = task.threshold
        # 
        # metatask = Task(0, name, self.hoursPerDay, threshold, interval, mp, cf)
        # metatask.primary = prime
        # metatask.days = self.bundleDays(bundle)
        
        # print "days:", metatask.days        
        metatask = Bundle(bundle)
        return metatask
        
    def withinInterval(self, schedule, asset, start, stupidcheckOn):
        """Check if a date falls within the interval period."""
        if stupidcheckOn:
            from objects.DateRange import DateRange

            interval = timedelta(days=self.interval)
            end = self.end(start)
            dates = schedule._scheduledTasks[asset.id].keys()

            before = DateRange(start - (interval - self.relax), start)
            after  = DateRange(end, end + (interval - self.relax))

            for date in dates:
                """If the task is scheduled for that date."""
                if self.id in schedule._scheduledTasks[asset.id][date]:
                    """Is the date found in the interval daterange?"""
                    if before.within(date):
                        return True
                    if after.within(date):
                        return True
        return False
