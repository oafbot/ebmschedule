from Task import Task
from math import ceil

class Bundle(Task):
    """A metatask class that is a wrapper for bundled tasks."""
    
    def __init__(self, tasks):
        Task.__init__(self, 0, "Bundle-", 0, 0, 0, [])
        self.tasks     = tasks  # The Tasks in the bundle.
        self.TasksMap  = {}     # Mappings of tasks to days.
        self.SkillsMap = {}     # Mappings of skill hours to days.
        self.contents  = []     # IDs of the tasks in the bundle.
        self.temp = 0
        
        self.initialize(tasks)
        self.calculateDays(tasks)
        self.allocate()
        self.distribute(tasks)
 
        print self.name, self.manhours, len(self.manpowers)
        for day in self.SkillsMap:
           for skill_id in self.SkillsMap[day]:
               skill = self.SkillsMap[day][skill_id]
               print day, ":", skill.name, skill.hours
        print ""

    def initialize(self, tasks):
        """Configure the basic properties of the bundle as a meta-task."""
        for task in tasks:
            """Inherit properties from primary task."""
            if task.primary:
                self.primary = task
                self.interval = task.interval
                self.threshold = task.threshold
                self.workday = self.hoursPerDay = task.hoursPerDay
            """self.contents will hold the IDs of the tasks that comprise the bundle."""
            self.contents.append(task.id)
            self.manpowers.extend(task.manpowers)
            # self.manhours += task.manhours
        self.name += str(self.primary.id)
        """aggergate manhours."""
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
        for day in range(0, self.days+1):
            if day not in self.SkillsMap:
                self.SkillsMap[day] = {}
            if day not in self.TasksMap:
                self.TasksMap[day] = []
            
    def getSkills(self, day):
        """Return the pooled skill hours for designated day."""
        pool = []
        for i in self.SkillsMap[day]:
            pool.append(self.SkillsMap[day][i])
        return pool
        
    def distribute(self, tasks):
        """Distribute conflicts and manpower hours to the corresponding days."""        
        remainder = 0 # remainder hours from the previous task
        start = 0     # start day
        end = 0       # end day
        for task in tasks:
            hours = remainder + task.duration()
            """As tasks occur serially within a bundle, 
            determine if the task carries over to the next day."""
            if hours >= self.workday:                
                end += int(hours / self.workday) # increment the end day
                remainder = hours % self.workday # remainder is assigned the modulus
            else:
                remainder = hours
            """Map skills and their hours to the day"""
            self.mapSkills(start, end, remainder, task)
            """Map the task to the appropriate day in the bundle."""
            start, end = self.mapTasks(remainder, start, end, task)

    def mapTasks(self, remainder, start, end, task):
        """Assign tasks to the corresponding days."""
        days = range(start, end+1) if remainder > 0 else range(start, end)
        for day in days:
            self.TasksMap[day].append(task.id) # Add task to the day
            # self.mapSkills(start, day, remainder, task)
        return [end, end]        
            
    def mapSkills(self, start, day, remainder, task):
        """Assign skill hours to appropriate days."""
        for skill in task.skills:
            for manpower in task.manpowers:
                if manpower.skill.id == skill.id:
                    workhours = manpower.hours
                    
                    # if remainder + workhours >= self.workday:
                    #     print remainder, "+", workhours, "=", remainder + workhours

                    if skill.id == 17: #or skill.id == 16:
                        self.temp += workhours
                        print start, remainder, "+", workhours, "=", remainder + workhours
                                        
                    if remainder + workhours <= self.workday:
                        hours = workhours
                        end = start
                        overhours = False
                    else:
                        mod = (remainder + workhours) % self.workday
                        end = start + int((remainder + workhours) / self.workday)                                 
                        overhours = True
                        
                    for day in range(start, end+1):
                        """If longer than a day and not the last day, apply full workday."""           
                        if overhours:
                            hours = workhours - mod if day < end else mod                             
                        elif day > start:
                            hours = 0
                        
                        if skill.id == 17:
                            print day, hours
                        
                        if skill.id in self.SkillsMap[day]:
                            if self.SkillsMap[day][skill.id].hours + hours <= skill.availableHours:
                                self.SkillsMap[day][skill.id].hours += hours
                            else:
                                hours -= (skill.availableHours - self.SkillsMap[day][skill.id].hours)
                                self.SkillsMap[day][skill.id].hours = skill.availableHours
                                                    
                                if day+1 not in self.SkillsMap:
                                    self.SkillsMap[day+1] = {}
                                if skill.id not in self.SkillsMap[day+1]:
                                    self.SkillsMap[day+1][skill.id] = skill.copy()
                                    self.SkillsMap[day+1][skill.id].hours = 0
                                self.SkillsMap[day+1][skill.id].hours += hours
                        else:
                            self.SkillsMap[day][skill.id] = skill.copy()
                            self.SkillsMap[day][skill.id].hours = hours