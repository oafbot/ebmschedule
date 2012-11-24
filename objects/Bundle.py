from Task import Task
from math import ceil

class Bundle(Task):
    """A metatask class that is a wrapper for bundled tasks."""
    
    def __init__(self, tasks):
        Task.__init__(self, 0, "", 0, 0, 0, [])
        self.tasks = tasks
        self.TasksMap = {}
        self.SkillsMap = {}
        self.ConflictsMap = {}
        self.contents = []
                
        self.initialize(tasks)
        self.calculateDays(tasks)
        self.distribute(tasks)

    def initialize(self, tasks):
        for task in tasks:
            if task.primary:
                self.primary = task
                self.interval = task.interval
                self.threshold = task.threshold
                self.workday = self.hoursPerDay = task.hoursPerDay
            self.name += str(task.id) + "-"
            self.contents.append(task.id)
            self.manpowers.extend(task.manpowers) 
        self.name = self.name[:-1]
        for manpower in self.manpowers:
            self.manhours += manpower.hours
    
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
    
    def calculateSkillHours(self, task):
        remainder = 0
        start = 0
        end = 0
        
        for day in range(0, self.days):
            """Allocate days to the Skills array."""
            if day not in self.SkillsMap:
                self.SkillsMap.update({day:[]})
            
        for skill in task.skills:
            """Calculate the days and the remainder."""
            if skill.hours < self.workday:
                remainder = skill.hours
            else:
                end = int(skill.hours / self.workday)
                remainder = skill.hours % self.workday
            """If the remainder is zero, don't apply to next day."""
            days = range(start, end+1) if remainder > 0 else range(start, end)

            for day in days:
                """Copy skill, adjust hours and store in array."""
                _skill = skill.copy()
                _skill.hours = remainder if remainder > 0 else self.workday
                self.SkillsMap[day].append(_skill)
            start = end
        
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
            
            skills = self.calculateSkillHours(task)                                
            start, end = self.assign(remainder, start, end, task, skills)
        
    def longest(self, task):
        """Find the the most time-costly aspect of a task and return its duration."""
        longest = 0
        for manpower in task.manpowers:                
            if manpower.hours > longest: longest = manpower.hours
        return longest
 
    def assign(self, remainder, start, end, task, skills):
        """Allocate constraints to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end)
        
        for day in days:
            if day not in self.ConflictsMap:
                self.ConflictsMap.update({day:task.conflicts})
            else:
                self.ConflictsMap[day].union(task.conflicts)
            if day not in self.TasksMap:
                self.TasksMap.update({day:[task.id]})
            else:
                self.TasksMap[day].append(task.id)            
        return [end, end]
