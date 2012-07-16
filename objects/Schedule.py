class Schedule:
    def __init__(self, dataSource, dateRange, maxAssetsInWork):
        self.dataSource = dataSource
        self.dateRange = dateRange
        self.maxAssetsInWork = maxAssetsInWork
        self._schedule = {}     #assets >> tasks
        self._assetsInWork = {} #date >> assets
        self._skillsInWork = {} #date >> skills
        self._scheduledTasks = {} #assets >> date >> tasks
        self._conflictTasks = {} #assets >> date >> conflicts
        self.totalManhours = 0

    def force(self, asset, task, dateRange):
        self._addToSchedule(asset, task.forceSchedule(dateRange))

    def add(self, asset, task, date):
        _task = task.schedule(date) #Create scheduled task
        self._addToSchedule(asset, _task)
        return _task.dateRange.end

    def blocked(self, asset, task, date):
        _task = task.schedule(date) #Create scheduled task (prevent threading issues)
        for date in _task.dateRange.range():
            if  date in self._assetsInWork.keys() and \
                len(set(self._assetsInWork[date]).difference([asset.id])) >= self.maxAssetsInWork:
                #difference: if Asset XYZ is already in set, then take it out before making this logic (in other words, if already scheduled in that day you can schedule additional tasks for that asset on that day
                #LHS is the number of assets *already* scheduled, so if >= maxAssets cannot schedule any additional assets
                return True
            for skill in task.skills:
                if  date in self._skillsInWork.keys() and \
                    skill.id in self._skillsInWork[date].keys() and \
                    self._skillsInWork[date][skill.id] + skill.hoursPerDay > skill.availableHours:
                    #print task.id, self._skillsInWork[date][skill.id], skill.hoursPerDay, skill.availableHours
                    return True

            if  asset.id in self._conflictTasks.keys() and \
                date in self._conflictTasks[asset.id].keys() and \
                task.id in self._conflictTasks[asset.id][date]:
                return True           
            
        return False

    def last(self, asset, task):
        if asset.id in self._schedule.keys():
            for _task in self._schedule[asset.id]:
                if _task.id == task.id:
                    return _task.dateRange.end
    
    def _addToSchedule(self, asset, task):
        
        if asset.id not in self._schedule: 
            self._schedule[asset.id] = []
        self._schedule[asset.id].append(task)
        
        for date in task.dateRange.range():
            
            if date not in self._assetsInWork.keys(): 
                self._assetsInWork[date] = [asset.id]
            elif asset.id not in self._assetsInWork[date]: 
                self._assetsInWork[date].append(asset.id)
                
            for skill in task.skills:
                if date not in self._skillsInWork.keys(): 
                    self._skillsInWork[date] = { skill.id:skill.hoursPerDay }
                elif skill.id not in self._skillsInWork[date].keys():
                    self._skillsInWork[date][skill.id] = skill.hoursPerDay
                else:
                    self._skillsInWork[date][skill.id] += skill.hoursPerDay
                    
            if asset.id not in self._scheduledTasks.keys(): 
                self._scheduledTasks[asset.id] = { date: [task.id] }
            elif date not in self._scheduledTasks[asset.id]: 
                self._scheduledTasks[asset.id][date] = [task.id]
            else:
                self._scheduledTasks[asset.id][date].append(task.id)
 
            if asset.id not in self._conflictTasks.keys(): 
                self._conflictTasks[asset.id] = { date: task.conflicts }
            elif date not in self._conflictTasks[asset.id]: 
                self._conflictTasks[asset.id][date] = task.conflicts
            else:
                self._conflictTasks[asset.id][date] = self._conflictTasks[asset.id][date].union(task.conflicts)

                
        self.totalManhours += task.manhours
        
    