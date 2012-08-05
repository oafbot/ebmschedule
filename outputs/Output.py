class Output:

    def __init__(self, input):
        self.input = input
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
                if task.conflicts:
                    print "Conflicts:       ",
                    for n in sorted(task.conflicts):
                        print str.ljust(str(n), 3),
                if task.prep:
                    print "\nPrep:            ",
                    for n in sorted(task.prep):
                        print str.ljust(str(n), 3),
                if task.prereq:
                    print "\nPrerequisite:    ",
                    for n in sorted(task.prereq):
                        print str.ljust(str(n), 3),
                if task.subseq:
                    print "\nSubsequent:      ",
                    for p in sorted(task.subseq):
                        print str.ljust(str(p), 3),
                if task.concur:
                    print "\nConcur:          ",
                    for n in sorted(task.concur):
                        print str.ljust(str(n), 3),        
                print "\n------------------------------------------------------------\n"    