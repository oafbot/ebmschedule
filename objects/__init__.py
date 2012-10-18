class Asset:    
    def __init__(self, id, name, start):
        self.id    = id
        self.name  = name
        self.start = start        
        
    def __contains__(self, assets): 
        for _asset in assets: 
            if _asset.id == self.id: 
                return True
        return False


class Skill:    
    def __init__(self, id, name, available, hoursPerDay):
        self.id             = id
        self.name           = name
        self.available      = available
        self.hoursPerDay    = hoursPerDay
        self.availableHours = available * hoursPerDay
        
    def copy(self):
        from copy import deepcopy
        return deepcopy(self)


class Manpower:    
    def __init__(self, id, skill, hours):
        self.id    = id
        self.skill = skill
        self.hours = hours
        
        
class Usage:
    def __init__(self):
        self.dates = {}
        # for date in daterange.range():
        #     self.schedule[date] = hours
        # self.schedule = sorted(self.schedule)
        
    def add(self, date, asset, usage):
        # if date not in self.schedule:
        #     self.schedule[date] = {}    
        # self.schedule[date].update({asset: usage})
        if (date, asset) not in self.dates:
            self.dates[(date, asset)] = usage
        else:
            # print date, self.dates[(date, asset)], usage
            self.dates[(date, asset)] += usage
        