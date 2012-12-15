class Schedule:
    
    def __init__(self, dataSource, dateRange, maxAssetsInWork, hours):
        from objects import Usage
        self.dataSource      = dataSource      # The model used for the scheduleing.
        self.dateRange       = dateRange       # The daterange for the scheduling cycle.
        self.hoursPerDay     = hours           # hours in a workday.
        self.maxAssetsInWork = maxAssetsInWork # maximum number of assets that can be worked on.
        self._schedule       = {}	           # assets >> tasks
        self._assetsInWork   = {}              # date   >> assets
        self._skillsInWork   = {}              # date   >> skills
        self._scheduledTasks = {}              # assets >> date >> tasks
        self._conflictTasks  = {}              # assets >> date >> conflicts
        self.forced          = []              # forced schedulings
        self.usage           = Usage()
        self.used            = []              # flag to indicate usage
        self.used_date       = None            # capture the date that is marked for usage
        self.used_asset      = None            # capture the asset being marked for usage 
        self.usageViolation  = 0               # count of usage violations
        self.totalManhours   = 0               # count of manhours
        self.cal             = None            # Google calendar object
        
    def force(self, asset, task, dateRange):
        """Force an asset to be scheduled for specified task to be performed."""
        self._addToSchedule(asset, task.forceSchedule(dateRange), 0, True)
        self.forced.append({'asset':asset.name,'task':task.name,
            'start':dateRange.start,'end':dateRange.end})
    
    def add(self, asset, task, date, remainder=0):
        """Add a task to a schedule and return the end date for the task."""
        _task = task.schedule(date) #Create scheduled task
        self._addToSchedule(asset, _task, remainder)
        return _task.dateRange.end

    def last(self, asset, task):
        """Last time task was performed on the asset. Return end date."""
        if asset.id in self._schedule.keys():
            for _task in self._schedule[asset.id]:
                if _task.id == task.id:
                    return _task.dateRange.end
    
    def blocked(self, asset, task, date, stupidity):
        """Return False if task can be scheduled on that day."""
        from datetime import timedelta
        """Create scheduled task to prevent threading issues."""
        _task = task.schedule(date)
        
        for delta, date in enumerate(_task.dateRange.range()):
            """Check the number of assets being worked on."""
            if self.checkAssets(date, asset): return True
            """Check usage requirements."""
            if self.checkUsage(date, asset): 
                # print "Usage:    ", date.date(), asset.id, task.id if task.id != 0 else task.name
                return True                
            """Check skills hours availability and usage."""
            if self.checkSkills(date, delta, asset, task): 
                # print "Skills:   ", date.date(), asset.id, task.id if task.id != 0 else task.name
                return True
            """Check conflicts."""
            if self.checkConflicts(date, delta, asset, task): 
                # print "Conflicts:", date.date(), asset.id, task.id if task.id != 0 else task.name
                return True
            """Check for overlapping and overscheduling.""" 
            if self.checkOverlaps(date, asset, task, stupidity): return True
        # print "scheduled:", date.date(), task.name if task.id == 0 else task.id
        return False
                    
    def checkAssets(self, date, asset):
        """Check the number of assets being worked on."""                       
        if date.date() in self._assetsInWork.keys():
            """If asset is already in set, take it out before running logic."""
            worked = set(self._assetsInWork[date.date()]).difference([asset.id])                
            if len(worked) >= self.maxAssetsInWork:
                return True
        return False
    
    def getUsage(self, date, asset):
        """Return usage amount required for that day."""
        if (date.date(), asset.id) in self.usage.dates:
            return self.usage.dates[(date.date(), asset.id)]
        return 0
    
    def checkUsage(self, date, asset):
        """Check on Usage requirements."""
        if self.getUsage(date, asset) > self.hoursPerDay:
            """If usage hours are greater than a workday, the day is blocked."""
            self.setUsage(date, asset)
            return True
        return False

    def setUsage(self, date, asset):
        """Set usage flags."""
        self.used.append(date.date())
    
    def unsetUsage(self):
        """Clear usage flags."""
        self.used = []
    
    def checkConflicts(self, date, delta, asset, task):
        """Check conflicts."""
        if asset.id in self._conflictTasks.keys() and date in self._conflictTasks[asset.id].keys():                                       
            if task.id == 0:
                """Check if there are conflicts in a bundle for that day.""" 
                for subtask in task.TasksMap[delta]:
                    if subtask in self._conflictTasks[asset.id][date]:
                        return True
            elif task.id in self._conflictTasks[asset.id][date]:
                """Check for conflicts for regularly scheduled tasks."""                    
                return True
        return False

    def checkOverlaps(self, date, asset, task, stupidity):
        """Check for overlapping and overscheduling."""
        if task.id != 0 and task.withinInterval(self, asset, date, stupidity):
            """If not a metatask check if task falls within the interval."""
            return True
        elif task.id == 0 and task.primary.withinInterval(self, asset, date, stupidity):
            """If a metatask, check if the primary task falls within the interval."""
            return True
        return False

    def checkSkills(self, date, delta, asset, task):
        """Check skills hours availability and usage."""
        from math import floor
        usage = self.getUsage(date, asset) # get usage hours
        skills = task.SkillsMap[delta]        
        self.skillsInWork = dict(self._skillsInWork)
        
        for skill in skills:            
            if skill.hours > skill.availableHours:
                """If the hours are more than available in a workday."""
                raise RuntimeError('Hours exceed maximum available resources.')
            
            """Calculate the available hours for the skill."""
            available = round(skill.hoursPerDay - usage, 2)            
            """If there were enough resources."""
            if (date, skill.id) in self.skillsInWork.keys():               
                availability = []
                for index, remaining in enumerate(self.skillsInWork[(date, skill.id)]):                        
                     if remaining >= skill.hours:
                         """If there were enough resources."""
                         availability.append(True)
                     else:
                         """If there were enough resources."""   
                         availability.append(False)
                if not any(avail):
                    """"If all availability evaluates to False there were enough resources."""
                    if usage > 0: self.setUsage(date, asset)
                    return True
                else:
                    sorted(self.skillsInWork[(date, skill.id)], reverse=True)[0] -= floor(skill.hours)
                    # round(self.skillsInWork[(date, skill.id)][0], 2)
                    # print sorted(self.skillsInWork[(date, skill.id)], reverse=True)                                 
            elif available < skill.hours:
                """If there were enough resources."""
                if usage > 0: self.setUsage(date, asset)
                return True
            else:
                self.skillsInWork[(date, skill.id)] = skill.resources(usage)
                self.skillsInWork[(date, skill.id)][0] -= floor(skill.hours)
                # print self.skillsInWork[(date, skill.id)], date.date()
        return False

    # from datetime import datetime
    # if datetime(2013,12,19).date() == date.date():                    
    #     print date.date(), any(avail), avail, self.skillsInWork[(date, skill.id)], skill.id, skill.hours

    def _addToSchedule(self, asset, task, remainder, forced=False):
        """Add a task to an asset in the schedule."""
        from datetime import datetime
        """Keep a record of assets and tasks scheduled."""
        if asset.id not in self._schedule:
            self._schedule[asset.id] = []
        self._schedule[asset.id].append(task)
        """Keep a record of skills and their hours scheduled."""
        self.scheduleSkills(task, remainder, task.dateRange.start, asset)
        
        for date in task.dateRange.range():                        
            """Assign asset to the date."""            
            if date.date() not in self._assetsInWork.keys():
                self._assetsInWork[date.date()] = [asset.id]
            elif asset.id not in self._assetsInWork[date.date()]:
                self._assetsInWork[date.date()].append(asset.id)
            """Assign asset, date, and task to list of scheduled tasks."""
            if asset.id not in self._scheduledTasks.keys():                
                self._scheduledTasks[asset.id] = { date: [task.id] }
            elif date not in self._scheduledTasks[asset.id]: 
                self._scheduledTasks[asset.id][date] = [task.id]
            else:
                self._scheduledTasks[asset.id][date].append(task.id)
            """Assign conflict to list of conflicts."""                 
            if asset.id not in self._conflictTasks.keys():
                self._conflictTasks[asset.id] = { date: task.conflicts }
            elif date not in self._conflictTasks[asset.id]: 
                self._conflictTasks[asset.id][date] = task.conflicts
            else:
                self._conflictTasks[asset.id][date] = \
                self._conflictTasks[asset.id][date].union(task.conflicts)
        
        """Tally manhours."""
        if task.dateRange.end <= self.dateRange.end and task.dateRange.start >= self.dateRange.start:
            self.totalManhours += task.manhours
        
        """Call Google Calendar scheduler."""
        from inputs.Config import Config
        if(Config().pushcal and not forced):
            self.scheduleCalendar(task,asset)

    def scheduleSkills(self, task, remainder, start, asset):
        """Assign skills and their hours to the date."""
        from datetime import timedelta
        from math import ceil
        from math import floor
        
        for manpower in task.manpowers:
            if manpower.hours + remainder <= task.hoursPerDay:
                """If the task fits within the day."""
                hours = manpower.hours
                last = 0
                days = 1
            else:
                """If the task goes over a day."""
                last  = round((manpower.hours + remainder) % task.hoursPerDay, 2) # hours for the last day
                days  = int(ceil((manpower.hours + remainder) / task.hoursPerDay))
                hours = round(task.hoursPerDay - remainder, 2) # hours for the first day
            
            for d in range(0, days):
                """Iterate through the days."""
                date  = start + timedelta(days=d)
                skill = manpower.skill
                
                if days > 1:
                    if d == days-1:
                        """If the day is last, apply the remainder."""
                        hours = last 
                    elif d != 0:
                        """If it's not the first day apply full workday."""
                        hours = task.hoursPerDay                   
                """"get usage hours"""
                usage = self.getUsage(date, asset)
                
                """Record the hours for the skill.""" 
                if (date, skill.id) not in self._skillsInWork.keys():                    
                    self._skillsInWork[(date, skill.id)] = skill.resources(usage)
                
                index = self.isAvailable(hours, (date, skill.id))
                if index is not None: 
                    self._skillsInWork[(date, skill.id)][index] -= floor(hours)
                    round(self._skillsInWork[(date, skill.id)][index], 2)
                else:
                    print "\n",self._skillsInWork[(date, skill.id)], date.date(), d, hours
                    raise RuntimeError("Skill Hours Distribution Mismatch Error")

                # if date >= self.dateRange.start and date <= self.dateRange.end:
                #     print self._skillsInWork[(date, skill.id)], skill.id, date.date(), d, hours
    
    def isAvailable(self, hours, key):
        for index, available in enumerate(sorted(self._skillsInWork[key], reverse=True)):
            if available >= hours:
                return index        
        return None
    
    def scheduleCalendar(self, task, asset):
        """Schedule to Google Calendar."""        
        from outputs.Calendar import Calendar
        from datetime import timedelta
        import gdata.service
        import time
        
        if not self.cal: self.cal = Calendar()
        calendar = self.cal.Select(asset.name)        
        start = task.dateRange.start.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end = task.dateRange.end + timedelta(minutes=1) # shift time for Google calendar display
        end = end.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        if start == end:            
            response_feed = self.cal.InsertSingleEvent(calendar, task.name, task.name, None, start)
        else:
            response_feed = self.cal.InsertSingleEvent(calendar, task.name, task.name, None, start, end)
