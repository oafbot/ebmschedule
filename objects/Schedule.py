class Schedule:
    
    def __init__(self, dataSource, dateRange, maxAssetsInWork, hours):
        from objects import Usage
        self.dataSource      = dataSource
        self.dateRange       = dateRange
        self.hoursPerDay     = hours
        self.maxAssetsInWork = maxAssetsInWork        
        self._schedule       = {}	# assets >> tasks
        self._assetsInWork   = {}   # date   >> assets
        self._skillsInWork   = {}   # date   >> skills
        self._scheduledTasks = {}   # assets >> date >> tasks
        self._conflictTasks  = {}   # assets >> date >> conflicts
        self.metrics         = {}
        self.forced          = []
        self.usage           = Usage()
        self.used            = False
        self.used_date       = None
        self.used_asset      = None
        self.totalUsage      = 0
        self.totalManhours   = 0        
        self.cal             = None
        
    def force(self, asset, task, dateRange):
        """Force an asset to be scheduled for specified task to be performed."""
        self._addToSchedule(asset, task.forceSchedule(dateRange),True)
        self.forced.append({'asset':asset.name,'task':task.name,
            'start':dateRange.start,'end':dateRange.end})
    
    def add(self, asset, task, date):
        """Add a task to a schedule and return the end date for the task."""
        _task = task.schedule(date) #Create scheduled task
        self._addToSchedule(asset, _task)
        return _task.dateRange.end
    
    def blocked(self, asset, task, date, stupidity):
        """Return False if task can be scheduled on that day."""
        from datetime import timedelta
        
        _task = task.schedule(date) #Create scheduled task (prevent threading issues)
        
        for delta, date in enumerate(_task.dateRange.range()):
            """Check the number of assets being worked on."""
            if (date.date() in self._assetsInWork.keys() and len(
               set(self._assetsInWork[date.date()]).difference([asset.id])) >= self.maxAssetsInWork):
               """Note on difference: If Asset Foo is already in set, then take it out before running this logic."""
                    return True
            
            """Check on Usage requirements."""
            if (date.date(), asset.id) in self.usage.dates:
                """Assign usage to the amount required on that day."""
                usage = self.usage.dates[(date.date(), asset.id)]
                if usage > self.hoursPerDay:
                    """If usage hours are greater than a workday. Return"""
                    self.used_date = date.date()
                    self.used_asset = asset.id
                    self.used = True
                    return True
            else:
                usage = 0
            
            """Check skills hours availability and usage."""
            if task.id != 0:
                for skill in task.skills:                    
                    """Check if the required skills are available."""
                    if(task.days <= 1):
                        """If the task can be completed in a day."""
                        hours = skill.hours
                    elif(delta == task.days-1):
                        """If it is the last day of a multi-day task."""
                        hours = skill.hours % skill.hoursPerDay
                    else:
                        """Otherwise schedule for full workday."""
                        hours = skill.hoursPerDay
                
                    """Calculate the available hours for the skill."""
                    available = skill.availableHours - (usage * skill.available)    

                    if(date in self._skillsInWork.keys() and skill.id in self._skillsInWork[date].keys()):
                        if self._skillsInWork[date][skill.id] + hours > available:
                            """If the sum of scheduled and current skill hours exceed available hours."""
                            if usage > 0: 
                                self.used_date = date.date()
                                self.used_asset = asset.id
                                self.used = True
                            return True
            else:
                for skill in task.SkillsMap[delta]:
                    """Check if the required skills are available."""
                    if(task.days <= 1):
                        """If the task can be completed in a day."""
                        hours = skill.hours
                    elif(delta == task.days-1):
                        """If it is the last day of a multi-day task."""
                        hours = skill.hours % skill.hoursPerDay
                    else:
                        """Otherwise schedule for full workday."""
                        hours = skill.hoursPerDay
                
                        """Calculate the available hours for the skill."""
                        available = skill.availableHours - (usage * skill.available)    
            
                        if(date in self._skillsInWork.keys() and skill.id in self._skillsInWork[date].keys()):
                            if self._skillsInWork[date][skill.id] + hours > available:
                                if usage > 0: 
                                    self.used_date = date.date()
                                    self.used_asset = asset.id
                                    self.used = True
                                return True
                        
            """Check conflicts."""
            if asset.id in self._conflictTasks.keys() and date in self._conflictTasks[asset.id].keys():                                       
                if task.id == 0:
                    """Check if there are conflicts in a bundle for that day."""
                    for subtask in task.TasksMap[delta]:
                        if subtask in self._conflictTasks[asset.id][date]:
                            return True
                elif task.id in self._conflictTasks[asset.id][date]:                    
                    return True
            
            """Check for overlapping and overscheduling."""
            if task.id != 0 and task.withinInterval(self, asset, date, stupidity):
                """If not a metatask check if task falls within the interval."""
                return True
            elif task.id == 0 and task.primary.withinInterval(self, asset, date, stupidity):
                """If a metatask, check if the primary task falls within the interval."""
                return True
                                
        return False
    
    def last(self, asset, task):
        """Last time task was performed on the asset. Return end date."""
        if asset.id in self._schedule.keys():
            for _task in self._schedule[asset.id]:
                if _task.id == task.id:
                    return _task.dateRange.end
                    
    def _addToSchedule(self, asset, task, forced = False):
        """Add a task to an asset in the schedule."""
        from datetime import datetime
        if asset.id not in self._schedule:
            self._schedule[asset.id] = []
        self._schedule[asset.id].append(task)
                        
        for date in task.dateRange.range():                        
            """Assign asset to the date."""               
            if date.date() not in self._assetsInWork.keys():
                self._assetsInWork[date.date()] = [asset.id]
            elif asset.id not in self._assetsInWork[date.date()]:
                self._assetsInWork[date.date()].append(asset.id)
                    
            for skill in task.skills:
                """Assign skills to the date."""
                if date not in self._skillsInWork.keys():
                    self._skillsInWork[date] = { skill.id:skill.hours }
                elif skill.id not in self._skillsInWork[date].keys():
                    self._skillsInWork[date][skill.id] = skill.hours
                else:
                    self._skillsInWork[date][skill.id] += skill.hours       
            
            if asset.id not in self._scheduledTasks.keys():
                """Assign asset, date, and task to list of scheduled tasks."""
                self._scheduledTasks[asset.id] = { date: [task.id] }
            elif date not in self._scheduledTasks[asset.id]: 
                self._scheduledTasks[asset.id][date] = [task.id]
            else:
                self._scheduledTasks[asset.id][date].append(task.id)
                            
            if asset.id not in self._conflictTasks.keys():
                """Assign conflict to list of conflicts.""" 
                self._conflictTasks[asset.id] = { date: task.conflicts }
            elif date not in self._conflictTasks[asset.id]: 
                self._conflictTasks[asset.id][date] = task.conflicts
            else:
                self._conflictTasks[asset.id][date] = \
                self._conflictTasks[asset.id][date].union(task.conflicts)

            """Tally manhours."""
            if date <= self.dateRange.end and date >= self.dateRange.start:
                self.totalManhours += task.manhours
                
                if (asset.id,task.id) not in self.metrics:                    
                    self.metrics.update({(asset.id,task.id):0})
                self.metrics[(asset.id,task.id)] += task.manhours
        
        """Call Google Calendar scheduler."""
        from inputs.Config import Config
        if(Config().pushcal and not forced):
            self.scheduleCalendar(task,asset)
    
    def scheduleCalendar(self, task, asset):
        """Schedule to Google Calendar."""        
        from outputs.Calendar import Calendar
        from datetime import timedelta
        import gdata.service
        import time
        
        if not self.cal: self.cal = Calendar()
        calendar = self.cal.Select(asset.name)        
        start = task.dateRange.start.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end = task.dateRange.end + timedelta(minutes=1) #shift time for Google calendar display
        end = end.strftime('%Y-%m-%dT%H:%M:%S.000Z')

        if start == end:            
            response_feed = self.cal.InsertSingleEvent(calendar, task.name, task.name, None, start)
        else:
            response_feed = self.cal.InsertSingleEvent(calendar, task.name, task.name, None, start, end)
