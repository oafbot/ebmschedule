from datetime import timedelta
from math import ceil

class Task:

    def __init__(self, id, name, workhours, threshold, interval, manpowers, 
                 conflicts=list(), prep=list(), prereq=list(), subseq=list(), concur=list()):

        self.id           = id
        self.name         = name
        self.threshold    = threshold
        self.interval     = interval
        self.manpowers    = manpowers      # array holding the manpower required
        self.conflicts    = set(conflicts) # set holding IDs of conflict tasks.
        self.prep         = set(prep)      # prepatory tasks
        self.prereq       = set(prereq)    # prerequisite tasks
        self.subseq       = set(subseq)    # subsequent tasks
        self.concur       = set(concur)    # concurrent tasks
        self.locked       = False
        self.hoursPerDay  = workhours      # hours in a workday
        self.skills       = []             # array holding all the required skills. Hours pooled
        self.SkillsMap    = {}             # Mappings of skill hours to days.
        self.days         = 0              # duration of a task in days
        self.manhours     = 0              # total manpower hours.
        self.score        = 0              # score given by the sorting algorithm
        self.child        = False          # flag for child tasks
        self.required     = False          # flag for required tasks
        self.preparatory  = False          # flag for prep tasks
        self.concurrent   = False          # flag for concurrent tasks
        self.primary      = False          # flag for primary tasks
        self.subsequent   = False          # flag for subsequent tasks
        self.reqInterval  = int(ceil(self.interval/2)) # interval for required tasks.
        self.relax        = timedelta(days=int(ceil(self.interval/4))) # easing for 'stupidity'-checking. Implementation off.

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
            self.days = int(max(self.days, ceil(manpower.hours / manpower.skill.hoursPerDay))) 
            # self.sumSkills(manpower)
            self.manhours += manpower.hours
        self.allocate()
        self.mapSkills()

    def tostring(self):
        """Output to console."""
        print self.name, self.manhours
        for day in self.SkillsMap:
           for skill in self.SkillsMap[day]:
               print day, ":", skill.name, skill.hours
        print ""

    def sumSkills(self, manpower):
        """If the skill is in the list of required skills add manpower hours."""
        newSkill = manpower.skill.copy()
        for _skill in self.skills:
            if newSkill.id == _skill.id:
                _skill.hours += manpower.hours
                return
        newSkill.hours = manpower.hours
        self.skills.append(newSkill)

    def duration(self):
        """Find the the most time-costly aspect of a task and return its duration."""
        longest = 0
        for manpower in self.manpowers:                
            if manpower.hours > longest: longest = manpower.hours
        return longest

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
                    if(not self.requisiteSatisfied(input.schedule, asset, t)):
                        bundle = self.bundle(bundle, self.prereq, asset, input)
        return bundle

    def requisiteSatisfied(self, schedule, asset, task, date=None):
        """Checks if a prerequisite has been performed within a designated timeframe."""
        if(date==None):
            date = schedule.dateRange.start
        last = schedule.last(asset, task)
        start = self.next(asset, schedule.last(asset, self))
        start = max(start, date)
        if(last is None):
            return False
        elif(last < start - timedelta(days=self.reqInterval)):
            return False
        return True

    def concurrence(self, bundle, asset, input):
        """Negotiate the appropriate scheduling for concurrent tasks."""
        concurlist = []
        tasks_set  = True

        for t in input.tasks:
            for c in self.concur:
                if t.id == c:
                    t.concurrent = True
                    concurlist.append(t)
        
        for concurrent in concurlist:
            """Check if tasks are already in the Bundle."""
            if concurrent not in bundle: tasks_set = False
        
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

    def allocate(self):
        """Allocate days to the mapping arrays."""
        for day in range(0, self.days):
            if day not in self.SkillsMap:
                self.SkillsMap[day] = []    

    def mapSkills(self):
        for manpower in self.manpowers:
            if manpower.hours > self.hoursPerDay:
                mod = manpower.hours % self.hoursPerDay
                hrs = self.hoursPerDay
                over = True
            else:
                hrs = manpower.hours
                over = False
            
            for day in range(0, self.days):
                if over:
                    """If longer than a day and last day, apply remainder."""
                    hours = hrs if day < self.days-1 else mod
                else:
                    """Apply 0 hours to all days after the first if shorter than a day."""
                    hours = 0 if day > 0 else hrs
                
                _skill = manpower.skill.copy()
                _skill.hours = round(hours, 2)
                self.SkillsMap[day].append(_skill)