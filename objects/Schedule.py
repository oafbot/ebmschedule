class Schedule:
    
    def __init__(self, dataSource, dateRange, maxAssetsInWork):
        self.dataSource      = dataSource
        self.dateRange       = dateRange
        self.maxAssetsInWork = maxAssetsInWork        
        self._schedule       = {}	# assets >> tasks
        self._assetsInWork   = {}   # date   >> assets
        self._skillsInWork   = {}   # date   >> skills
        self._scheduledTasks = {}   # assets >> date >> tasks
        self._conflictTasks  = {}   # assets >> date >> conflicts
        self.totalManhours   = 0
        self.forced          = []        
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
    
    def blocked(self, asset, task, date):
        """Return False if task can be scheduled on that day."""
        _task = task.schedule(date) #Create scheduled task (prevent threading issues)
        
        for date in _task.dateRange.range():
            """
            difference: If Asset Foo is already in set, 
            then take it out before running this logic. i.e. If already scheduled, 
            one can schedule additional tasks for that asset on that day.
            
            LHS is the number of assets *already* scheduled, so if >= maxAssets cannot 
            schedule any additional assets
            """
            if  date in self._assetsInWork.keys() and \
                len(set(self._assetsInWork[date]).difference([asset.id])) \
                    >= self.maxAssetsInWork:
                return True
            
            for skill in task.skills:
                if  date in self._skillsInWork.keys() and \
                    skill.id in self._skillsInWork[date].keys() and \
                    self._skillsInWork[date][skill.id] + \
                        skill.hoursPerDay > skill.availableHours:
                    return True
            
            if asset.id in self._conflictTasks.keys() and \
                date in self._conflictTasks[asset.id].keys():
                    if task.id in self._conflictTasks[asset.id][date]:
                        return True
                    """Catch outside case where task is a Meta-task."""
                    if task.id == 0:
                        meta = task.name.split("-")
                        while '' in meta:
                            meta.remove('')
                        for meta_id in meta:
                            if int(meta_id) in self._conflictTasks[asset.id][date]: return True

            """If not a metatask check if task falls within the interval."""
            if task.id != 0 and task.withinInterval(self, asset, date):
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
        if asset.id not in self._schedule:
            self._schedule[asset.id] = []
        self._schedule[asset.id].append(task)
        
        for date in task.dateRange.range():
            """Assign asset to the date."""
            if date not in self._assetsInWork.keys():
                self._assetsInWork[date] = [asset.id]
            elif asset.id not in self._assetsInWork[date]:
                self._assetsInWork[date].append(asset.id)
            
            for skill in task.skills:
                """Assign skills to the date."""
                if date not in self._skillsInWork.keys():
                    self._skillsInWork[date] = { skill.id:skill.hoursPerDay }
                elif skill.id not in self._skillsInWork[date].keys():
                    self._skillsInWork[date][skill.id] = skill.hoursPerDay
                else:
                    self._skillsInWork[date][skill.id] += skill.hoursPerDay
            
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
        self.totalManhours += task.manhours
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
