from Task import Task
from math import ceil

class Bundle(Task):
    def __init__(self, tasks):
        Task.__init__(self, 0, "", 0, 0, 0, [])
        self.tasks = tasks
        self.TasksMap = {}
        self.ConflictsMap = {}
        self.ManpowersMap = {}        
        self.contents = []
        
        self.initialize(tasks)
        self.distribute(tasks)
        self.calculateDays(tasks)
        print self.days

    def initialize(self, tasks):
        for task in tasks:
            if task.primary:
                self.primary = task
                self.interval = task.interval
                self.threshold = task.threshold
                self.workday = self.hoursPerDay = task.hoursPerDay
            self.name += str(task.id) + "-"
            self.contents.append(task.id)
        self.name = self.name[:-1]
    
    def calculateDays(self, bundle):
        """Return the number of days a bundle of tasks takes to perform."""
        hours = []
        for task in bundle:
            longest = 0
            for manpower in task.manpowers:
                """Find the the most costly task."""
                if manpower.hours > longest: longest = manpower.hours
            hours.append(longest)
        self.days = int(ceil(sum(hours) / self.hoursPerDay))
    
    def tasksInBundle():
        """Return an array of tasks associated with the bundle."""
        meta = self.name.split("-")
        while '' in meta:
            meta.remove('')
        return meta
    
    def distribute(self, tasks):
        """Distribute conflicts and manpower hours to the corresponding days."""        
        remainder = 0
        start = 0
        end = 0                
        for task in tasks:
            hours = self.longest(task)
            hours = remainder + hours                        
            if hours >= self.workday:
                end += int(hours / self.workday)
                remainder = hours % self.workday
            else:
                remainder = hours                                
            start, end = self.allocate(remainder, start, end, task)
    
    def longest(self, task):
        """Find the the most time-costly aspect of a task and return its duration."""
        longest = 0
        for manpower in task.manpowers:                
            if manpower.hours > longest: longest = manpower.hours
        return longest
 
    def allocate(self, remainder, start, end, task):
        """Allocate constraints to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end) 
        
        for day in days:
            if day not in self.conflicts:
                self.TasksMap.update({day:[task.id]})
                self.ConflictsMap.update({day:task.conflicts})
            else:
                self.TasksMap[day].append(task.id)
                self.ConflictsMap[day].union(task.conflicts)       
        return [end, end]
