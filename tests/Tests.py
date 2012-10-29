from datetime import timedelta
from datetime import datetime
from collections import namedtuple
from objects.DateRange import DateRange
# from collections import Counter
# import thread

class Tests:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.metrics   = self.algorithm.metrics
        self.output    = self.algorithm.output
        self.model     = self.algorithm.results
        self.schedule  = self.model.schedule
        self.tasks     = self.model.tasks
        self.assets    = self.model.assets        
        self.total     = 0
        self.stopwatch = datetime.now()
        
        self.IntervalCheck()
    
    def IntervalCheck(self):                
        """Find and flag interval violations."""
        Index = namedtuple("Index", ["Asset", "Task"])
        SortedByTask = self.SortByTask(Index)        
        self.IntervalViolations(SortedByTask)        
        self.console("Summary", [self.violation, self.ground, self.ineff, self.average])
            
    def SortByTask(self, Index):
        """Sort the schedule by Asset and Task."""
        SortedByTask = {}
        count = 0.00

        for asset in self.assets:
            dates = self.schedule._scheduledTasks[asset.id].keys()
            
            for n, date in enumerate(dates):                
                self.output.statusbar(count, len(self.assets), "Processed")                                                
                
                for task in self.tasks:
                    if task.id in self.schedule._scheduledTasks[asset.id][date]:
                        """If the task is in the schedule for that day."""
                        if( Index(Asset=asset.id, Task=task.id) not in SortedByTask):
                            SortedByTask[Index(Asset=asset.id, Task=task.id)] = []
                        
                        for t in self.schedule._schedule[asset.id]:
                            if(t.dateRange.start == date and date not in 
                                SortedByTask[Index(Asset=asset.id, Task=task.id)]):
                                SortedByTask[Index(Asset=asset.id, Task=task.id)].append(date)
                                self.total += 1
            count += 1.00
        self.output.lineout("Processed: |" + "==|" * 10 + " 100%")
        return SortedByTask
    
    def IntervalViolations(self, SortedByTask):
        """Find and print out interval violations."""
        SortedIndecies = sorted(SortedByTask)
        prev = None
        prev_asset = None
        prev_task = None
        self.violation = 0
        self.ground = 0
        self.ineff  = 0
        active = set()
        self.grounded = []
        self.terminated = True
        self.console("Banner", None)
        
        for i in SortedIndecies:
            """Iterate through the Tupple Indicies."""            
            prev = None
            daterange = None
            
            for a in self.assets:                    
                """Find the corresponding Asset."""
                if(a.id == i.Asset): asset = a  
            for t in self.tasks:
                """Find the corresponding Task."""
                if(t.id == i.Task): task = t                       
            if(asset.id != prev_asset):
                """If it is a new Asset, reset the set containing dates Asset is worked on."""
                active = set()
                self.console("Asset", asset.name)
            
            prev_asset = asset.id
            SortedByTask[i].sort(key=lambda d: (d.year, d.month, d.day))
                        
            for date in SortedByTask[i]:
                if(prev is None or date < asset.start):
                    prev = date                
                elif(date >= asset.start and date <= self.schedule.dateRange.end and date > task.end(prev) and date not in active):
                    if(task.interval > 0 and not task.child):
                        """Do not count concurrent, subsequent, prep and prereq tasks."""
                        for d in DateRange(date, task.end(date)).range(): active.update([d])
                        difference = (date - prev).days
                                                
                        if(difference != timedelta(days=task.interval).days):
                            """If the difference is not the same as the interval."""                                                                                                                
                            self.violation += 1
                           
                            if(difference - task.interval > 0):
                                """Count groundings if non-consecutive and distinct."""
                                self.ground += 1
                                self.grounded.append(drift)
                                drift = difference - task.interval
                            else:
                                """Count inefficiencies if non-consecutive and distinct."""
                                self.ineff += 1
                                drift = difference - task.interval
                                                           
                            if(abs(drift) > 7):
                                """Output to console."""                            
                                self.console("Task", [task, prev, date, difference, drift])
                    
                    """Increment previous task date."""
                    prev = task.end(date)
                else:
                    prev = date                            
        self.average = sum(self.grounded)/len(self.grounded) if len(self.grounded) > 0 else 0
    
    def setMetrics(self):
        self.metrics.DataSource      = self.schedule.dataSource
        self.metrics.Algorithm       = self.algorithm.name
        self.metrics.Weight          = self.algorithm.weight
        self.metrics.Data            = self.model.count
        self.metrics.Manhours        = self.schedule.totalManhours
        self.metrics.Usage           = self.schedule.totalUsage
        self.metrics.UsageTotal      = len(self.schedule.usage.dates)
        self.metrics.UsageCount      = self.schedule.usage.count
        self.metrics.Groundings      = self.ground
        self.metrics.Inefficiencies  = self.ineff
        self.metrics.Scheduled       = self.total
        self.metrics.Violations      = self.violation
        self.metrics.Optimal         = self.total - self.violation
        self.metrics.AverageGround   = self.average
        self.metrics.ExtendedGround  = sum(n > 7 for n in self.grounded)
        self.metrics.Available       = self.schedule._assetsInWork
        self.metrics.end             = self.schedule.dateRange.end
        self.metrics.start           = self.schedule.dateRange.start
                
    def console(self, type, args):
        if(self.model.conf.testout):
            if(type=="Banner"):
                print "\n-------------------------------------------\
                       \n------------- INTERVAL CHECKS -------------\
                       \n-------------------------------------------"
        
            elif(type == "Asset"):
                print "\nAsset:", args, "\n-------------------------------------------"
        
            elif(type == "Task"):
                task, prev, date, difference, drift = args                
                drift = self.output.hilite("+"+str(drift), 0) if drift > 0 else self.output.hilite(drift)
        
                print "Task: " + str(task.id), task.name
                print "Last:", str(task.end(prev))[:-9], "\tInterval:   ", \
                       self.output.strfdelta(timedelta(days=task.interval), "{days} days")
                print "Date:", str(date)[:-9], \
                      "\tDifference: ", difference, "days\t", str.rjust(str(drift), 6)
                print "-------------------------------------------"
                
        if(type == "Summary"):
            violation, ground, ineff, average = args
            print str.ljust(" " * 33 + "Execution: " + \
                  str(datetime.now()-self.stopwatch)[:-4], 25), "\n\n" + \
                  str.ljust("Scheduled:", 10), str.ljust(str(self.total), 10), \
                  str.ljust("Optimal:", 10), str.ljust(str(self.total - violation), 10), \
                  str.ljust("Violation:", 10), str.ljust(str(violation), 10), \
                  str.ljust("Grounding:", 10), str.ljust(str(ground), 10), \
                  str.ljust("Inefficiency:", 10), str.ljust(str(ineff), 10) + "\n" + \
                  str.ljust("Manhours:", 10), str.ljust(str(self.schedule.totalManhours), 10), \
                  str.ljust("Average:", 10), str.ljust(str(average) + " days", 10), \
                  str.ljust("Usage:", 10), str.ljust(str(self.schedule.totalUsage), 10) + "\n"
