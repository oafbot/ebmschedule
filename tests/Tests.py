from datetime import timedelta
from datetime import datetime
from collections import namedtuple
from objects.DateRange import DateRange

class Tests:
    def __init__(self, model):
        self.schedule = model.schedule
        self.tasks = model.tasks
        self.assets = model.assets
        self.oneday = timedelta(days=1)
        
        scheduled = self.schedule._scheduledTasks
                
        SortedByTask = {}
        Index = namedtuple("Index", ["Asset", "Task"])
        
        for asset in self.assets:
            """Sort the schedule by Asset and Task."""
            dates = scheduled[asset.id].keys() 
            dates.sort(key=lambda d: (d.year, d.month, d.day))
            
            for date in dates:
                for task in model.tasks:
                    if task.id in scheduled[asset.id][date]:
                        """If the task is in the schedule for that day."""
                        if( Index(Asset=asset.id, Task=task.id) not in SortedByTask):
                            SortedByTask[Index(Asset=asset.id, Task=task.id)] = []
                        for t in self.schedule._schedule[asset.id]:
                            if(t.dateRange.start == date):
                                SortedByTask[Index(Asset=asset.id, Task=task.id)].append(date)
            
        SortedIndecies = sorted(SortedByTask)
        prev = None
        prev_asset = None
        prev_task = None        
        # print SortedIndecies
        # print SortedByTask
        counter = 0
        for i in SortedIndecies:
            prev = None
            daterange = None
            """Iterate through the Tupple Indicies."""
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
                    
            # print i 
            # for d in SortedByTask[i]:
            #     print d

            for date in SortedByTask[i]:                
                if(prev is None or date < asset.start):
                    prev = date
                elif(date >= asset.start and task.interval > 0 and date > task.end(prev)):
                    difference = (date - prev).days
                    if(difference != timedelta(days=task.interval-1).days and difference != timedelta(days=task.interval).days):
                        """If the difference is not the same as the interval."""
                        # print "Violation"
                        print "Task: " + str(task.id), task.name
                        print "Date:", str(date)[:-9], "\tInterval:\t", self.strfdelta(timedelta(days=task.interval), "{days} days") 
                        print "Last:", str(task.end(prev))[:-9], "\tDifference:\t", difference, "days"
                        # print "Interval:", self.strfdelta(timedelta(days=task.interval), "{days} days")
                        # print "Difference:", self.strfdelta(difference, "{days} days")
                        print "-------------------------------------------"
                        counter += 1
                    prev = task.end(date)
                else:
                    prev = None
        print "\nTotal Violations:", counter
                        

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)