from Task import Task
from math import ceil

class Bundle(Task):
    """A metatask class that is a wrapper for bundled tasks."""
    
    def __init__(self, tasks):
        Task.__init__(self, 0, "Bundle-", 0, 0, 0, [])
        self.tasks     = tasks
        self.TasksMap  = {}
        self.SkillsMap = {}
        self.contents  = []
        
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
        # for day in self.SkillsMap:
        #    for skill_id in self.SkillsMap[day]:
        #        skill = self.SkillsMap[day][skill_id]
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
            longest = task.duration()
            hours.append(longest)
        self.days = int(ceil(sum(hours) / self.hoursPerDay))
            
    def allocate(self):
        """Allocate days to the mapping arrays."""
        for day in range(0, self.days):            
            # if day not in self.SkillsMap:
            #     self.SkillsMap.update({day:[]})
            if day not in self.SkillsMap:
                self.SkillsMap.update({day:{}})
            if day not in self.TasksMap:
                self.TasksMap.update({day:[]})
            
    def pooledSkills(self, day):
        """Return the pooled skill hours for designated day."""
        pooled = []
        for i in self.SkillsMap[day]:
            pooled.append(self.SkillsMap[day][i])
        return pooled

        
    def distribute(self, tasks):
        """Distribute conflicts and manpower hours to the corresponding days."""        
        remainder = 0
        start = 0
        end = 0
        for task in tasks:           
            hours = remainder + task.duration()
            if hours >= self.workday:
                end += int(hours / self.workday)
                remainder = hours % self.workday
            else:
                remainder = hours
            start, end = self.mapTasks(remainder, start, end, task)
        
            
    def mapSkills(self, start, day, task):
        """Assign skill hours to appropriate days."""        
        for skill in task.skills:
            for manpower in task.manpowers:
                if manpower.skill.id == skill.id:
                    workhours = manpower.hours
                    end = start
                    if workhours < self.workday:
                        remainder = workhours if day == start else 0
                    else:
                        end += int(workhours / self.workday)
                        remainder = workhours % self.workday
                """Copy skill, adjust hours and store in array."""            
                hours = self.workday if end > start and day < end else remainder

                if skill.id in self.SkillsMap[day]:
                    if self.SkillsMap[day][skill.id].hours + hours <= skill.availableHours:
                        self.SkillsMap[day][skill.id].hours += hours
                    else:
                        self.SkillsMap[day][skill.id].hours = skill.availableHours
                        if day+1 not in self.SkillsMap:
                            self.SkillsMap.update({day+1:{}})
                        if skill.id not in self.SkillsMap[day+1]:
                            _skill = skill.copy()
                            self.SkillsMap[day+1].update({_skill.id:_skill})
                        self.SkillsMap[day+1][skill.id].hours += hours % skill.availableHours
                else:
                    _skill = skill.copy()
                    self.SkillsMap[day].update({_skill.id:_skill})
                
                # print day, task.id, skill.id, hours, self.SkillsMap[day][skill.id].hours
        
    def mapTasks(self, remainder, start, end, task):
        """Assign constraints to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end)
        for day in days:
            self.TasksMap[day].append(task.id)
            self.mapSkills(start, day, task)
        return [end, end]
