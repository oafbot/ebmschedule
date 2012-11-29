from Task import Task
from math import ceil

class Bundle(Task):
    """A metatask class that is a wrapper for bundled tasks."""
    
    def __init__(self, tasks):
        Task.__init__(self, 0, "Bundle-", 0, 0, 0, [])
        self.tasks = tasks
        self.TasksMap = {}
        self.SkillsMap = {}
        self.SkillsPool = {}
        self.contents = []
                
        self.calculateDays(tasks)
        self.initialize(tasks)
        self.distribute(tasks)
                
        # print self.name
        # for day in self.SkillsMap:
        #    for skill in self.SkillsMap[day]:
        #        print day, ":", skill.name, skill.hours
        # print ""
        # 
        # print self.name
        # for day in self.SkillsPool:
        #    for skill_id in self.SkillsPool[day]:
        #        skill = self.SkillsPool[day][skill_id]
        #        print day, ":", skill.name, skill.hours
        # print ""

    def initialize(self, tasks):
        for task in tasks:
            if task.primary:
                """Inherit from primary task."""
                self.primary = task
                self.interval = task.interval
                self.threshold = task.threshold
                self.workday = self.hoursPerDay = task.hoursPerDay
            self.contents.append(task.id)
            # self.manpowers.extend(task.manpowers)
        self.name += str(self.primary.id)
        
        for manpower in self.manpowers:
            self.manhours += manpower.hours
    
        for day in range(0, self.days):
            """Allocate days to the Skills array."""
            if day not in self.SkillsMap:
                self.SkillsMap.update({day:[]})
            if day not in self.SkillsPool:
                self.SkillsPool.update({day:{}})
    
    def calculateDays(self, bundle):
        """Return the number of days a bundle of tasks takes to perform."""
        hours = []
        for task in bundle:
            longest = self.longest(task)
            hours.append(longest)
        self.days = int(ceil(sum(hours) / self.hoursPerDay))
    
        
    def calculateSkillHours(self, task):
        remainder = 0
        start = 0
        end = 0
        
        for day in range(0, self.days):
            """Allocate days to the Skills array."""
            if day not in self.SkillsMap:
                self.SkillsMap.update({day:[]})
            if day not in self.SkillsPool:
                self.SkillsPool.update({day:{}})
            
        for skill in task.skills:
            """Calculate the days and the remainder."""
            if skill.hours <= skill.availableHours:
                end = 0
                remainder = skill.hours
            else:
                end = int(skill.hours / skill.availableHours)
                remainder = skill.hours % skill.availableHours
            """If the remainder is zero, don't apply to next day."""
            days = range(start, end+1) if remainder > 0 else range(start, end)
            
            # print end, ":", skill.hours, remainder
            
            for day in days:
                """Copy skill, adjust hours and store in array."""
                _skill = skill.copy()
                _skill.hours = skill.availableHours if end > 0 and day < end else remainder
                
                # self.SkillsMap[day].append(_skill)
                
                if _skill.id in self.SkillsPool[day]:
                    self.SkillsPool[day][_skill.id].hours += _skill.hours
                else:
                    self.SkillsPool[day].update({_skill.id:_skill})
    
    def pooledSkills(self, day):
        """Return the pooled skill hours for designated day."""
        pooled = []
        for i in self.SkillsPool[day]:
            pooled.append(self.SkillsPool[day][i])
        return pooled

        
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

            # self.calculateSkillHours(task)
            start, end = self.assign(remainder, start, end, task)

    def longest(self, task):
        """Find the the most time-costly aspect of a task and return its duration."""
        longest = 0
        for manpower in task.manpowers:                
            if manpower.hours > longest: longest = manpower.hours
        return longest

    def assign(self, remainder, start, end, task):
        """Allocate constraints to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end)

        for day in days:
            if day not in self.TasksMap:
                self.TasksMap.update({day:[task.id]})
            else:
                self.TasksMap[day].append(task.id)
            
            for skill in task.skills:
                if skill.hours <= skill.availableHours:
                    """Copy skill, adjust hours and store in array."""
                    _skill = skill.copy()
                    if _skill.id in self.SkillsPool[day]:
                        self.SkillsPool[day][_skill.id].hours += _skill.hours
                    else:
                        self.SkillsPool[day].update({_skill.id:_skill})
                else:
                    end = int(skill.hours / skill.availableHours)
                    remainder = skill.hours % skill.availableHours
            
        return [end, end]
