from datetime import datetime
from datetime import timedelta

class Metrics:
    def __init__(self):
        self.DataSource   = None
        self.Algorithm    = None
        self.Weight       = None
        self.Data         = None
        self.Manhours        = 0
        self.Usage           = 0
        self.UsageTotal      = 0
        self.Imminent        = 0
        self.UsageCount      = 0
        self.ActualGround    = 0 # discrete count
        self.Groundings      = 0 # raw count
        self.GroundedSum     = 0 # raw count
        self.Inefficiencies  = 0
        self.Scheduled       = 0
        self.Violations      = 0
        self.Optimal         = 0
        self.AverageGround   = 0        
        self.ExtendedGround  = 0
        self.NumberOfAssets  = 0
        self.Forced          = 0
        self.Available       = {}

        self.costas = {}
        
    def set(self, algorithm):                
        self.algorithm = algorithm
        self.output    = self.algorithm.output
        self.model     = self.algorithm.results
        self.schedule  = self.model.schedule
        self.tasks     = self.model.tasks
        self.assets    = self.model.assets        
        self.stopwatch = datetime.now()
        
        self.DataSource = self.schedule.dataSource
        self.Algorithm  = self.algorithm.name
        self.Weight     = self.algorithm.weight
        self.Data       = self.model.count
        self.Sort       = self.algorithm.sorting
        self.Manhours   = self.schedule.totalManhours        
        self.Scheduled  = self.algorithm.totalScheduled
        self.Available  = self.schedule._assetsInWork
        self.Usage      = self.schedule.totalUsage
        self.UsageTotal = len(self.schedule.usage.dates)
        self.UsageCount = self.schedule.usage.count
        
        self.end = self.schedule.dateRange.end
        self.start = self.schedule.dateRange.start
    
    def run(self, algorithm):        
        self.set(algorithm)
        self.calc()
        self.console()
        if self.model.conf.metrics:
            self.writeout()
    
    def calc(self):
        over = []
        under = []
        optimal = []
        for drift in self.algorithm.drift:
            if drift > timedelta(days=0):
                over.append(drift.days)
            elif drift < timedelta(days=0):
                under.append(drift.days)
            else:
                optimal.append(drift.days)

        self.Groundings = len(over)
        self.GroundedSum = sum(over)
        self.Inefficiencies = len(under)
        self.Optimal = len(optimal)
        self.Violations = len(self.algorithm.drift)-len(optimal)
        self.ExtendedGround = sum(n > 7 for n in over)
        self.AverageGround = sum(over)*1.0/len(over) if len(over) > 0 else 0
        
        total = 0
        for asset in self.costas:
            for ground in self.costas[asset]:
                total += self.costas[asset][ground]
        
        for ground in sorted(self.algorithm.groundings):
            # print ground
            self.ActualGround += self.algorithm.groundings[ground]
        
        print total
        print self.ActualGround
        
    def availability(self):
        from collections import Counter
        counts = []
        for date in self.Available:
            if date < self.end.date() and date >= self.start.date():
                counts.append(len(self.Available[date]))
        counter = Counter(counts)
        availables = ""
        for i in reversed(range(0, self.NumberOfAssets+1)):
            availables += "," + str(counter[i]) if i in counter else ",0"
        return availables

    def console(self):
        print str.ljust("Scheduled:", 10), str.ljust(str(self.Scheduled), 10), \
              str.ljust("Optimal:", 10), str.ljust(str(self.Optimal), 10), \
              str.ljust("Violation:", 10), str.ljust(str(self.Violations), 10), \
              str.ljust("Grounding:", 10), str.ljust(str(self.Groundings), 10), \
              str.ljust("Inefficiency:", 10), str.ljust(str(self.Inefficiencies), 10) + "\n" + \
              str.ljust("Manhours:", 10), str.ljust(str(self.Manhours), 10), \
              str.ljust("Average:", 10), str.ljust("{0:.1f}".format(self.AverageGround) + " days", 10), \
              str.ljust("Usage:", 10), str.ljust(str(self.Usage), 10), \
              str.ljust("Extended:", 10), str.ljust(str(self.ExtendedGround), 10), \
              str.ljust("Sort:", 5), str.ljust(self.Sort, 5) + "\n"
    
    def writeout(self):
        """Write out metrics to a file."""
        import os
        path = "../metrics/" if 'tools' in os.getcwd() else "metrics/"
        # percent = round((float(optimal) / float(self.total)) * 100, 2)
        fo = open(path + self.DataSource + ".csv", "ab+")
        if os.stat(path + self.DataSource + ".csv")[6]==0:
            header = ""
            for n in reversed(range(0, self.NumberOfAssets+1)):
                header += "," + str(self.NumberOfAssets - n) + " Avail."
            csv = "Algorithm,Data,Weight,Sort,Manhours,Grounded Days,Ground Raw Count,Grounding Events,Inefficiencies,Scheduled," + \
                  "Violations,Optimal,Average,Usage Viol.,Imminent Usg.,Planned Usg.,Extended Grnd" + \
                  header + "\n"
        else: 
            csv = ""
        csv += self.Algorithm                       + "," + \
               str(self.Data)                       + "," + \
               str(self.Weight)                     + "," + \
               str(self.Sort)                       + "," + \
               str(self.Manhours)                   + "," + \
               str(self.ActualGround)               + "," + \
               str(self.GroundedSum)                + "," + \
               str(self.Groundings)                 + "," + \
               str(self.Inefficiencies)             + "," + \
               str(self.Scheduled)                  + "," + \
               str(self.Violations)                 + "," + \
               str(self.Optimal)                    + "," + \
               "{0:.2f}".format(self.AverageGround) + "," + \
               str(self.Usage)                      + "," + \
               str(self.Imminent)                   + "," + \
               str(self.UsageTotal)                 + "," + \
               str(self.ExtendedGround)             + \
               self.availability()                  + "\n"
        fo.write(csv)
        fo.close()
