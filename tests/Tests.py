from datetime import timedelta
from datetime import datetime
from collections import namedtuple
from objects.DateRange import DateRange
# import thread

class Tests:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.model = self.algorithm.results
        self.schedule = self.model.schedule
        self.tasks = self.model.tasks
        self.assets = self.model.assets        
        self.total = 0
        self.stopwatch = datetime.now()
        # self.computed = 0
        # self.terminated = False
        # self.status = 0
        self.IntervalCheck()
        self.ConflictCheck()
    
    def IntervalCheck(self):                
        """Find and flag interval violations."""
        Index = namedtuple("Index", ["Asset", "Task"])
        SortedByTask = self.SortByTask(Index)
        self.IntervalViolations(SortedByTask)
    
    def Timer(self):
        import time
        counter = 0
        start = datetime.now()
        while(not self.terminated):
            d = datetime.now() - start
            print str(d.seconds/60)+":"+str(d.seconds%60)
        #     # time.sleep(2)
        #     counter += 1
        #     print counter
            
        
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
                                self.total += 1
        return SortedByTask
    
    def IntervalViolations(self, SortedByTask):
        """Find and print out interval violations."""
        SortedIndecies = sorted(SortedByTask)
        prev = None
        prev_asset = None
        prev_task = None
        violation = 0
        ground = 0
        ineff  = 0
        groundedlist = []
        self.terminated = True
        
        if(self.model.conf.testout):
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
                if(self.model.conf.testout):
                    print "\nAsset:", asset.name
                    print "-------------------------------------------"
            prev_asset = asset.id
            
            SortedByTask[i].sort(key=lambda d: (d.year, d.month, d.day))

            for date in SortedByTask[i]:                
                if(prev is None or date < asset.start):
                    prev = date
                elif(date >= asset.start and task.interval > 0 and 
                     date > task.end(prev) and not task.concurrent):
                    """Do not count concurrent tasks."""
                    difference = (date - prev).days
                    if(difference != timedelta(days=task.interval-1).days and 
                       difference != timedelta(days=task.interval).days):
                        """If the difference is not the same as the interval."""
                        # if(self.model.conf.trace and abs(difference - task.interval) > 7):
                        diff = difference - task.interval
                        drift = self.hilite("+"+str(diff), 0) if diff > 0 else self.hilite(diff)
                        
                        if(self.model.conf.testout and abs(diff) > 0):
                            print "Task: " + str(task.id), task.name
                            print "Last:", str(task.end(prev))[:-9], "\tInterval:   ", \
                                   self.strfdelta(timedelta(days=task.interval), "{days} days")
                            print "Date:", str(date)[:-9], \
                                  "\tDifference: ", difference, "days\t", str.rjust(drift, 6)
                            print "-------------------------------------------"
                        violation += 1
                        if(difference - task.interval > 0):
                            ground += 1
                            daysgrounded = difference - task.interval
                            groundedlist.append(daysgrounded)
                        else:
                            ineff += 1
                    prev = task.end(date)
                else:
                    prev = None
        average_grounded = sum(groundedlist)/len(groundedlist) if len(groundedlist) > 0 else 0
        
        print "\n" + \
              str.ljust("Violations: " + str(violation), 25) + \
              str.ljust("Groundings: " + str(ground), 25) + \
              str.ljust("Inefficiencies:   " + str(ineff), 25 ) + "\n" + \
              str.ljust("Scheduled:  " + str(self.total), 25) + \
              str.ljust("Optimal:    " + str(self.total - violation), 25) + \
              str.ljust("Average grounded: " + str(average_grounded) + " days", 25 ), \
              str.ljust("Execution: " + str(datetime.now()-self.stopwatch)[:-4], 25)
                
        if(self.model.conf.metrics):
            self.writeMetrics(violation, ground, ineff, average_grounded)
        
    def writeMetrics(self, violations, groundings, inefficiencies, average_grounded):
        """Write out metrics to a file."""
        import os
        if 'tools' in os.getcwd(): 
            path = "../metrics/"
        else: 
            path = "metrics/"
        optimal = self.total - violations
        percent = round((float(optimal) / float(self.total)) * 100, 2)
        fo = open(path + self.schedule.dataSource + ".txt", "ab+")
        out =  str.ljust("Groundings: " + str(groundings), 25) + \
               str.ljust("Inefficiencies: " + str(inefficiencies), 25) + "\n" + \
               str.ljust("Scheduled: " + str(self.total), 25) + \
               str.ljust("Violations: " + str(violations), 25) + \
               str.ljust("Optimal: " + str(optimal) + "  " + str(percent) + "%", 25) + "\n" + \
               str.ljust("Average groundings: " + str(average_grounded) + " days", 25) + "\n"       
        fo.write(out)
        fo.close()
              
    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)
    
    def hilite(self, txt, status=True, bold=True):
        import sys
        if sys.stdout.isatty():
            attr = []
            if status:
                attr.append('32') #green
            else:
                attr.append('31') #red
            if bold:
                attr.append('1')
            return '\033[%sm%s\x1b[0m' % (';'.join(attr), txt)
        return txt