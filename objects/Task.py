class Task:
    
    def __init__(self, id, name, unit, threshold, interval, manpowers, 
                 conflicts, prep, prereq, subseq, concur):                                 
        self.id                  = id
        self.name                = name
        self.unit                = unit
        self.threshold           = threshold
        self.interval            = interval
        self.manpowers           = manpowers
        self.conflicts           = set(conflicts)
        self.prep                = set(prep)
        self.prereq              = set(prereq)
        self.subseq              = set(subseq)
        self.concur              = set(concur)
        self.locked              = False
        self.hoursPerDay         = 8
        self.skills              = []
        self.days                = 0
        self.manhours            = 0
        self.totalAvailableHours = 0
        self.bundled             = False # Ugly hack, but will have to do
        
        if len(manpowers): self.precal() #TODO: Should come from sequencing
        
    def next(self, asset, date):
        """
        If date is not set, return the start date plus the number of days 
        stipulated by the threshold.
        Otherwise return the latter of:
         A. date plus the delta of interval
         B. start date plus the delta of threshold  
        """
        #TODO: Add usage units
        #TODO: Add task start/end
        #TODO: Add schedule start/end/active
        if date == None: return self.addDays(asset.start, self.threshold)
        return max(self.addDays(date, self.interval), self.addDays(asset.start, self.threshold))
        # without rebasing it would be: return self.addDays(date, self.interval) 

    def end(self, start):
        """Calculate end date based on start date plus number of days task takes."""
        return self.addDays(start, self.days)
         
    def dateRange(self, date):
        """Set the date range"""
        from objects.DateRange import DateRange
        self.dateRange = DateRange(date, self.end(date))
    
    def addDays(self, date, days):
        """Return the sum of the date and the time difference between today and 'days'-1."""
        from datetime import timedelta
        from math import floor
        days -= 1 #commented out because of scheduling paradox for end date.
        return date + timedelta(days=floor(days)) #todo: decrement precision if decimal

    def precal(self):
        """Round to the next interger day for required skill."""
        from math import ceil
        for manpower in self.manpowers:
            #TODO: Don't hard-code
            self.days = ceil(max(self.days, manpower.hours / (manpower.skill.hoursPerDay *1.0))) 
            self.sumSkills(manpower)
            self.manhours += manpower.hours
            self.totalAvailableHours += manpower.skill.availableHours
    
    def sumSkills(self, manpower):
        """If the skill is in the list of required skills add manpower hours."""
        newSkill = manpower.skill.copy()
        for _skill in self.skills:
            if newSkill.id == _skill.id:
                _skill.total += manpower.hours
                return
        newSkill.total = manpower.hours
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
    
    def checkConstraints(self, bundle, asset, input):
        """Check the constrains and bundle tasks together when appropriate."""
        if self.prereq: self.satisfyRequisite(bundle, asset, input)              # prerequisite
        if self.prep: bundle = self.bundle(bundle, self.prep, asset, input)      # prepatory
        if not bundle or self not in bundle: bundle.append(self)                 # primary task
        if self.concur: bundle = self.concurrence(bundle, asset, input)          # concurrent
        if self.subseq: bundle = self.bundle(bundle, self.subseq, asset, input)  # subsequent
        return bundle
    
    def satisfyRequisite(self, bundle, asset, input):
        """Find out if a prerequisite has been satisfied. If not schedule the prerequisite."""
        from datetime import timedelta
        start = self.next(asset, input.schedule.last(asset, self))
        start = max(start, input.schedule.dateRange.start)
        requirelist = []
        """Find the task associated with the requisite id."""
        for t in input.tasks:
            for r in self.prereq:
                if t.id == r: 
                    t.bundled = True # Ugly hack, but will have to do given the original code
                    requirelist.append(t)
        """For every requirement, find out if it has been performed within the interval."""
        for require in requirelist:
            if input.schedule.last(asset, require) == None or (
               input.schedule.last(asset, require) + timedelta(days=require.interval) <= start 
               and input.schedule.last(asset, require) >= 
               require.end(start) + timedelta(days=require.interval)
            ): bundle = self.bundle(bundle, self.prereq, asset, input)
        return bundle             
    
    def concurrence(self, bundle, asset, input):
        """Negotiate the appropriate scheduling for concurrent tasks."""
        from datetime import timedelta
        start = self.next(asset, input.schedule.last(asset, self))
        start = max(start, input.schedule.dateRange.start)
        concurlist = []
        tasks_set  = False
        
        for t in input.tasks:
            for c in self.concur:
                if t.id == c: 
                    t.bundled = True # Ugly hack, but will have to do given the original code
                    concurlist.append(t)
        """Check if tasks are already in the Bundle."""
        for concurrent in concurlist:            
            if concurrent in bundle: tasks_set = True 
            else: tasks_set = False
        for concurrent in concurlist:
            """If all tasks are in the bundle return the bundle."""
            if tasks_set and self in bundle:
                return bundle
            """If no prior scheduling or scheduled prior to interval."""
            if input.schedule.last(asset, concurrent) == None or (
               input.schedule.last(asset, concurrent) + 
               timedelta(days=concurrent.interval) <= start and
               input.schedule.last(asset, concurrent) > 
               concurrent.end(start) + timedelta(days=concurrent.interval)
            ): bundle = self.bundle(bundle, self.concur, asset, input)
        return bundle
        
    def bundle(self, bundle, tasks, asset, input):
        """Bundle related tasks together."""
        for t in tasks:
            for task in input.tasks:
                if task.id == t: 
                    task.checkConstraints(bundle, asset, input)
                    if bundle and task not in bundle: return bundle.append(task)
        return bundle 

    def bundleAsTask(self, bundle, asset):
        """Convert a bundle into a meta-task for running schedule calculations."""
        from objects.Task import Task
        total = 0
        mp = []
        cf = []
        name = ""
        threshold = 0
        interval = 0
        for task in bundle:
            for manpower in task.manpowers:
                total += manpower.hours
                mp += task.manpowers
            cf += task.conflicts
            name += str(task.id) + " "
            if task.threshold > threshold: threshold = task.threshold
            if task.interval > interval: interval = task.interval
            #print task.name, task.manhours, total
        days = total / task.hoursPerDay
        return Task(0, "Bundle: "+name, 1, threshold, interval, mp, cf, 
                   list(), list(), list(), list())
                   
    def withinInterval():
        pass
