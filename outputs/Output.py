class Output:

    def __init__(self, input):
        self.input = input
        if input.bigdata:
            self.columnSize = 10
        else: 
            self.columnSize = 3
        self.trace = input.trace
        
    def console(self):
        """Print output to console."""        
        if self.trace:
            print ""
            print "Schedule:     No. " + str(self.input.count)
            print "Data source: ", self.input.schedule.dataSource
            print "Date range:  ", self.input.schedule.dateRange.start, ' -- ',                \
                                   self.input.schedule.dateRange.end
            print "Max assets in work: ", self.input.schedule.maxAssetsInWork
            print "------------------------------------------------------------\n"        
        
            for asset in self.input.assets:        
                print "Asset: ", asset.name 
                print "Start: ", asset.start
                print "------------------------------------------------------------\n"
        
            for skill in self.input.skills:
                print "Skill:           ", skill.name
                print "Availability:    ", skill.available
                print "Hours per day:   ", skill.hoursPerDay
                print "Available hours: ", skill.availableHours
                print "------------------------------------------------------------\n"
        
            for task in self.input.tasks:
                if task.id is not 0:
                    print "Task:            ", task.name
                    print "ID:              ", task.id
                    print "Unit:            ", task.unit
                    print "Threshold:       ", task.threshold
                    print "Interval:        ", task.interval
                    print "Days:            ", task.days
                    for m in task.manpowers:
                        print "Manpower:        ",m.hours, "x", m.skill.name 
                    if not self.input.bigdata:
                        if task.conflicts:
                            print "Conflicts:       ",
                            for n in sorted(task.conflicts):
                                print str.ljust(str(n), self.columnSize),
                        if task.prep:
                            print "\nPrep:            ",
                            for n in sorted(task.prep):
                                print str.ljust(str(n), self.columnSize),
                        if task.prereq:
                            print "\nPrerequisite:    ",
                            for n in sorted(task.prereq):
                                print str.ljust(str(n), self.columnSize),
                        if task.subseq:
                            print "\nSubsequent:      ",
                            for p in sorted(task.subseq):
                                print str.ljust(str(p), self.columnSize),
                        if task.concur:
                            print "\nConcur:          ",
                            for n in sorted(task.concur):
                                print str.ljust(str(n), self.columnSize),        
                        print "\n------------------------------------------------------------\n"
                    else:
                        if task.conflicts:
                            print "Conflicts:       ",
                            i = 0
                            for n in sorted(task.conflicts):
                                if i % 8 == 0:
                                    print ""
                                print str.ljust(str(n), self.columnSize),
                                i += 1
                        if task.prep:
                            print "\nPrep:            ",
                            i = 0
                            for n in sorted(task.prep):
                                if i % 8 == 0:
                                    print ""
                                print str.ljust(str(n), self.columnSize),
                                i += 1
                        if task.prereq:
                            print "\nPrerequisite:    ",
                            i = 0
                            for n in sorted(task.prereq):
                                if i % 8 == 0:
                                    print ""
                                print str.ljust(str(n), self.columnSize),
                                i += 1
                        if task.subseq:
                            print "\nSubsequent:      ",
                            i = 0
                            for p in sorted(task.subseq):
                                if i % 8 == 0:
                                    print ""
                                print str.ljust(str(p), self.columnSize),
                                i += 1
                        if task.concur:
                            print "\nConcur:          ",
                            i = 0
                            for n in sorted(task.concur):
                                if i % 8 == 0:
                                    print ""
                                print str.ljust(str(n), self.columnSize),
                                i += 1        
                        print "\n------------------------------------------------------------\n"
        
        for forced in self.input.schedule.forced:
            print "Force Schedule"
            print "Asset: ", forced['asset']
            print "Task:  ", forced['task']
            print "Dates: ", forced['start'], " - ", forced['end']
            print "------------------------------------------------------------\n"
                    
    def printSchedule(self, algorithm, asset, task, start, end):
        if self.input.bigdata:
            if algorithm.prev != asset.name: print ""
            print str.ljust(asset.name, 8), str.ljust(task.name, 96), \
            str.ljust(str(start)[:-9], 10), "--", \
            str.ljust(str(end)[:-9], 10)
            # str.ljust(str(task.interval), 8), \
            # str.ljust(str(task.interval), 8),     \
            # str.ljust(str(task.manhours), 8),     \
            # str.ljust(str(task.id), 8),           \
            algorithm.prev = asset.name
   
        else:
            if algorithm.prev != asset.name: print ""
            print str.ljust(asset.name, 16),                                                   \
                  str.ljust(task.name, 32),                                                    \
                  str.ljust(str(start)[:-9], 10), "--",                                        \
                  str.ljust(str(end)[:-9], 10)
            algorithm.prev = asset.name
    
    def writeMetrics(self, input, conflicts, name, weight, exectime, now):
        import os
        if 'tools' in os.getcwd():
            path = "../metrics/"
        else: 
            path = "metrics/"
        line = "\n----------------------------------------"+ \
               "-----------------------------------------\n"
        fo = open(path + input.schedule.dataSource + ".txt", "ab+")
        out = line+ name + ": " + input.schedule.dataSource + " " + str(input.count) + \
              "\t[" + str(now)[:-7] + "]" + "\tExecution: " + exectime + line + \
              "Weight: " + str(weight) + "\n" + \
              str.ljust("Manhours: " + str(input.schedule.totalManhours), 25) + \
              str.ljust("Adjustments: " + str(conflicts), 25) + "\n"

        fo.write( out )
        fo.close()
        
    def strfdelta(self, tdelta, fmt):
        """Convert timedelta to days."""
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    def hilite(self, txt, status=True, bold=True):
        """Hilite text in color terminals."""
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
        """Dynamic single line output."""
        length = len(str(output))
        delete = "\b" * (length + 1)
        print "{0}{1:{2}}".format(delete, output, length),

    def statusbar(self, numerator, denominator, label):
        """Progress bar rendering."""
        import sys
        if sys.stdout.isatty():
            perc = numerator/denominator
            bar  = ": |" + "==|" * int(perc*10) + int(10-(perc*10))*"---" + " "
            self.lineout(label + bar + str(int(perc*100))+"%")        