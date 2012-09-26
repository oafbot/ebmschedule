from datetime import timedelta
from datetime import datetime
from collections import namedtuple
from objects.DateRange import DateRange

class Tests:
    def __init__(self, model):
        self.schedule = model.schedule
        self.tasks = model.tasks
        self.assets = model.assets        
        self.IntervalCheck()
        self.ConflictCheck()
    
    def IntervalCheck(self):                
        """Find and flag interval violations."""
        Index = namedtuple("Index", ["Asset", "Task"])       
        SortedByTask = self.SortByTask(Index)
        self.IntervalViolations(SortedByTask)
        
    def ConflictCheck(self):
        pass
        
    def SortByTask(self, Index):
        """Sort the schedule by Asset and Task."""
        SortedByTask = {}
        for asset in self.assets:
            dates = self.schedule._scheduledTasks[asset.id].keys() 
            dates.sort(key=lambda d: (d.year, d.month, d.day))
            
            for date in dates:
                for task in self.tasks:
                    if task.id in self.schedule._scheduledTasks[asset.id][date]:
                        """If the task is in the schedule for that day."""
                        if( Index(Asset=asset.id, Task=task.id) not in SortedByTask):
                            SortedByTask[Index(Asset=asset.id, Task=task.id)] = []
                        for t in self.schedule._schedule[asset.id]:
                            if(t.dateRange.start == date):
                                SortedByTask[Index(Asset=asset.id, Task=task.id)].append(date)
        return SortedByTask
    
    def IntervalViolations(self, SortedByTask):
        """Find and print out interval violations."""
        SortedIndecies = sorted(SortedByTask)
        prev = None
        prev_asset = None
        prev_task = None
        counter = 0
        
        print "\n-------------------------------------------\
               \n------------- INTERVAL CHECKS -------------\
               \n-------------------------------------------"
        
        for i in SortedIndecies:
            """Iterate through the Tupple Indicies."""
            prev = None
            daterange = None
                        
            for a in self.assets:                    
                """Find the corresponding Asset."""
                if(a.id == i.Asset):
                    asset = a  
            for t in self.tasks:
                """Find the corresponding Task."""
                if(t.id == i.Task):
                    task = t
            if(asset.id != prev_asset):
                """If it is a new Asset, reset date."""
                print "\nAsset:", asset.name
                print "-------------------------------------------"
            prev_asset = asset.id
            
            SortedByTask[i].sort(key=lambda d: (d.year, d.month, d.day))

            for date in SortedByTask[i]:                
                if(prev is None or date < asset.start):
                    prev = date
                elif(date >= asset.start and task.interval > 0 and date > task.end(prev)):
                    difference = (date - prev).days
                    if(difference != timedelta(days=task.interval-1).days and 
                       difference != timedelta(days=task.interval).days):
                        """If the difference is not the same as the interval."""
                        print "Task: " + str(task.id), task.name
                        print "Date:", str(date)[:-9], "\tInterval:\t", \
                               self.strfdelta(timedelta(days=task.interval), "{days} days") 
                        print "Last:", str(task.end(prev))[:-9], \
                              "\tDifference:\t", difference, "days"
                        print "-------------------------------------------"
                        counter += 1
                    prev = task.end(date)
                else:
                    prev = None
        print "\nTotal Interval Violations:", counter

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)