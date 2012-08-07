class Output:

    def __init__(self, input):
        self.input = input
        if input.bigdata:
            self.columnSize = 10
        else: 
            self.columnSize = 3
        if input.trace:
            self.console()
    
    def console(self):
        """Print output to console."""        
        print ""
        print "Schedule"
        print "Data source: ", self.input.schedule.dataSource
        print "Date range:  ", self.input.schedule.dateRange.start, ' -- ',                    \
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
            print str.ljust(asset.name, 8), str.ljust(task.name, 112),                         \
                  str.ljust(str(start)[:-9], 10), "--",                                        \
                  str.ljust(str(end)[:-9], 10)
            algorithm.prev = asset.name      
        else:
            if algorithm.prev != asset.name: print ""
            print str.ljust(asset.name, 16),                                                   \
                  str.ljust(task.name, 32),                                                    \
                  str.ljust(str.replace(str(start), "00:00:00", ""), 10), "--",                \
                  str.ljust(str.replace(str(end), "00:00:00", ""), 10)
            algorithm.prev = asset.name
