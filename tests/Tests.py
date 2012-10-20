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
        self.IntervalCheck()
    
    def IntervalCheck(self):                
        """Find and flag interval violations."""
        Index = namedtuple("Index", ["Asset", "Task"])
        SortedByTask = self.SortByTask(Index)
        self.IntervalViolations(SortedByTask)
            
    def SortByTask(self, Index):
        """Sort the schedule by Asset and Task."""
        SortedByTask = {}
        count = 0.00

        for asset in self.assets:
            dates = self.schedule._scheduledTasks[asset.id].keys()
            
            for n, date in enumerate(dates):                
                self.statusbar(count, len(self.assets), "Processed")                                                
                
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
        self.lineout("Processed: |" + "==|" * 10 + " 100%\n")
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
        active = set()
        groundedlist = []
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
                elif(date >= asset.start and task.interval > 0 and date > task.end(prev)):
                    if date not in active and not task.concurrent:
                        """Do not count concurrent tasks."""
                        difference = (date - prev).days
                    
                        if(difference != timedelta(days=task.interval-1).days and
                           difference != timedelta(days=task.interval).days):
                            """If the difference is not the same as the interval.""" 
                            active.update([date])
                            drift = difference - task.interval
                            violation += 1
                        
                            if(difference - task.interval > 0):
                                ground += 1
                                daysgrounded = difference - task.interval
                                groundedlist.append(daysgrounded)
                            elif not task.subseq and not task.prereq:
                                ineff += 1
                        
                            if(abs(drift) > 7):                            
                                self.console("Task", [task, prev, date, difference, drift])
                    """Increment previous task date."""
                    prev = task.end(date)
                else:
                    prev = date
        
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
    
    def lineout(self, output):
        length = len(str(output))
        delete = "\b" * (length + 1)
        print "{0}{1:{2}}".format(delete, output, length),
    
    def statusbar(self, numerator, denominator, label):
        import sys
        if sys.stdout.isatty():
            perc = numerator/denominator
            bar  = ": |" + "==|" * int(perc*10) + int(10-(perc*10))*"---" + " "
            self.lineout(label + bar + str(int(perc*100))+"%")
            
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
                drift = self.hilite("+"+str(drift), 0) if drift > 0 else self.hilite(drift)
        
                print "Task: " + str(task.id), task.name
                print "Last:", str(task.end(prev))[:-9], "\tInterval:   ", \
                       self.strfdelta(timedelta(days=task.interval), "{days} days")
                print "Date:", str(date)[:-9], \
                      "\tDifference: ", difference, "days\t", str.rjust(str(drift), 6)
                print "-------------------------------------------"