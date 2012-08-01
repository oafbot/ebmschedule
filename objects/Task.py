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
        self.skills              = [] #init value
        self.days                = 0  #init value
        self.manhours            = 0  #init value
        self.totalAvailableHours = 0  #init value
        
        if len(manpowers): self.precal() #TODO: Should come from sequencing
                
        # Console Output -----------------------------------------------------
        print "Task:            ", self.name
        print "ID:              ", self.id
        print "Unit:            ", self.unit
        print "Threshold:       ", self.threshold
        print "Interval:        ", self.interval
        print "Days:            ", self.days
        for m in self.manpowers:
            print "Manpower:        ",m.hours, "x", m.skill.name 
        if self.conflicts:
            print "Conflicts:       ",
            for n in sorted(self.conflicts):
                print str.ljust(str(n), 3),
        if self.prep:
            print "\nPrep:            ",
            for n in sorted(self.prep):
                print str.ljust(str(n), 3),
        if self.prereq:
            print "\nPrerequisite:    ",
            for n in sorted(self.prereq):
                print str.ljust(str(n), 3),
        if self.subseq:
            print "\nSubsequent:      ",
            for p in sorted(self.subseq):
                print str.ljust(str(p), 3),
        if self.concur:
            print "\nConcur:          ",
            for n in sorted(self.concur):
                print str.ljust(str(n), 3),        
        print "\n------------------------------------------------------------\n"
        # --------------------------------------------------------------------
        
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
    
    def checkConstraints(self, bundle):
        #if self.prereq: bundle = self.bundle(bundle, self.prereq) # if prerequisite tasks exist
        if self.prep: bundle = self.bundle(bundle, self.prep)     # if prepatory tasks exist
        if not bundle or self not in bundle: bundle.append(self)  # append primary task
        if self.subseq: bundle = self.bundle(bundle, self.subseq) # if subsequent tasks exist
        return bundle
        
    def bundle(self, bundle, tasks):
        import main
        input = main.inputs.inputs[0].tasks
        for n in tasks:
            for task in input:
                if task.id == n: 
                    task.checkConstraints(bundle)
                    if bundle and task not in bundle: return bundle.append(task)
        return bundle 
        
    def reset(self):
        pass