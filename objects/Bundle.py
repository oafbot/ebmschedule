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
        
        self.initialize(tasks)
        self.calculateDays(tasks)
        self.allocate()
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
    
    def calculateDays(self, bundle):
        """Return the number of days a bundle of tasks takes to perform."""
        hours = []
        for task in bundle:
            longest = self.longest(task)
            hours.append(longest)
        self.days = int(ceil(sum(hours) / self.hoursPerDay))
    
    def longest(self, task):
        """Find the the most time-costly aspect of a task and return its duration."""
        longest = 0
        for manpower in task.manpowers:                
            if manpower.hours > longest: longest = manpower.hours
        return longest
        
    def allocate(self):
        """Allocate days to the mapping arrays."""
        for day in range(0, self.days):            
            if day not in self.SkillsMap:
                self.SkillsMap.update({day:[]})
            if day not in self.SkillsPool:
                self.SkillsPool.update({day:{}})
            if day not in self.TasksMap:
                self.TasksMap.update({day:[]})
            
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
            hours = remainder + self.longest(task)
            if hours >= self.workday:
                end += int(hours / self.workday)
                remainder = hours % self.workday
            else:
                remainder = hours
            start, end = self.mapTasks(remainder, start, end, task)
        
            
    def mapSkills(self, start, day, task):
        """Assign skill hours to appropriate days."""        
        for skill in task.skills:
            # resources = 0
            # for manpower in task.manpowers:
            #     if manpower.skill.id == skill.id:
            #         resources += 1
            for manpower in task.manpowers:
                if manpower.skill.id == skill.id:
                    workhours = manpower.hours
                    # resources = skill.hours / workhours
                    # print skill.hours, workhours, resources
                    end = start
                    if workhours < self.workday:
                        remainder = workhours if day == start else 0
                    else:
                        end += int(workhours / self.workday)
                        remainder = workhours % self.workday
                """Copy skill, adjust hours and store in array."""            
                hours = self.workday if end > start and day < end else remainder

                if skill.id in self.SkillsPool[day]:
                    self.SkillsPool[day][skill.id].hours += hours
                else:
                    _skill = skill.copy()
                    self.SkillsPool[day].update({_skill.id:_skill})
                
                # print day, task.id, skill.id, hours, self.SkillsPool[day][skill.id].hours
        
    def mapTasks(self, remainder, start, end, task):
        """Assign constraints to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end)
        for day in days:
            self.TasksMap[day].append(task.id)
            self.mapSkills(start, day, task)
        return [end, end]
