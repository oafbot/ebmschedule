from datetime import datetime
from datetime import timedelta

class Metrics:
    def __init__(self):
        self.DataSource   = None 
        self.Algorithm    = None 
        self.Weight       = None 
        self.Data         = None # dataset number
        self.Manhours        = 0 # total manhours.
        self.Usage           = 0 # usage violation count
        self.UsageTotal      = 0 # total planned usage for all assets.
        self.Imminent        = 0 # usage violation in the first 14 days. 
        self.Midterm         = 0 # usage violation in first 90 days.
        self.UsageCount      = 0 # structure holding assets and their planned usage count.
        self.ActualGround    = 0 # discrete count: summation of days grounded.
        self.Groundings      = 0 # discrete count: events where groundings occurred.
        self.GroundedSum     = 0 # raw count: summation of days grounded. Ovelaps unflitered.
        self.Inefficiencies  = 0 # raw count: summation of days scheduled prior to optimal date.
        self.Scheduled       = 0 # total number of scheduled tasks.
        self.Violations      = 0 # number of days tasks were not scheduled on optimal date
        self.Optimal         = 0 # number of days / events scheduled on optimal date.
        self.AverageGround   = 0 # average length of day assets were grounded
        self.ExtendedGround  = 0 # days that assets were grounded over 7 days.
        self.NumberOfAssets  = 0 # total number of assets.
        self.Forced          = 0 # count of forced schedulings.
        self.Available       = {} # availability of assets through the calendar cycle.
        
    def set(self, algorithm):
        """Set the basic properties for the metrics object."""               
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
        self.Scheduled  = self.algorithm.totalSched
        self.Available  = self.schedule._assetsInWork
        self.Usage      = self.schedule.usageViolation
        self.UsageTotal = len(self.schedule.usage.dates)
        self.UsageCount = self.schedule.usage.count
        
        self.end = self.schedule.dateRange.end
        self.start = self.schedule.dateRange.start
    
    def run(self, algorithm):
        """Run metrics calculations."""
        self.set(algorithm)
        self.calc()
        self.console()
        if self.model.conf.metrics:
            self.writeout()
    
    def calc(self):
        """Calculate groundings, optimal, inefficiencies."""
        over    = [] # groundings
        under   = [] # ineffiencies
        optimal = [] # optimal
        for drift in self.algorithm.drift:
            if drift > timedelta(days=0):
                over.append(drift.days)    # scheduled after the optimal date
            elif drift < timedelta(days=0):
                under.append(drift.days)   # scheduled before the optimal date
            else:
                optimal.append(drift.days) # scheduled on the optimal date
        # self.Groundings = len(over)
        self.GroundedSum = sum(over)
        self.Inefficiencies = abs(sum(under))
        self.Optimal = len(optimal)
        self.Violations = len(self.algorithm.drift)-len(optimal)
        self.ExtendedGround = sum(n > 7 for n in over)
        self.AverageGround = sum(over)*1.0/len(over) if len(over) > 0 else 0
        
        for ground in sorted(self.algorithm.groundings):
            self.ActualGround += self.algorithm.groundings[ground]
        
    def availability(self):
        """Determine the availability of assets throughout the scheduling cycle."""
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
        """Print metrics to the screen."""        
        print str.ljust("Scheduled:", 10), str.ljust(str(self.Scheduled), 10), \
              str.ljust("Optimal:", 10), str.ljust(str(self.Optimal), 10), \
              str.ljust("Violation:", 10), str.ljust(str(self.Violations), 10), \
              str.ljust("Grounding:", 10), str.ljust(str(self.ActualGround), 10), \
              str.ljust("Inefficiency:", 10), str.ljust(str(self.Inefficiencies), 10) + "\n" + \
              str.ljust("Manhours:", 10), str.ljust(str(self.Manhours), 10), \
              str.ljust("Average:", 10), str.ljust("{0:.1f}".format(self.AverageGround) + " days", 10), \
              str.ljust("Usage:", 10), str.ljust(str(self.Usage), 10), \
              str.ljust("Extended:", 10), str.ljust(str(self.ExtendedGround), 10), \
              str.ljust("Sort:", 5), str.ljust(self.Sort, 5) + "\n"
        # print str.ljust("Manhours:", 10), str.ljust(str(self.Manhours), 10), \
        #       str.ljust("Grounding:", 10), str.ljust(str(self.ActualGround), 5), \
        #       str.ljust("Usage:", 5), str.ljust(str(self.Usage), 5), \
        #       str.ljust("Sort:", 5), str.ljust(self.Sort, 5) + "\n"
    
    def writeout(self):
        """Write out metrics to a CSV file."""
        import os
        """determine path and open file for writing."""
        path = "../metrics/" if 'tools' in os.getcwd() else "metrics/"
        fo = open(path + self.DataSource + ".csv", "ab+")
        if os.stat(path + self.DataSource + ".csv")[6]==0:
            """If the file is new or empty, write out the header containing all field names."""
            header = ""
            for n in reversed(range(0, self.NumberOfAssets+1)):
                """Create field names for availability depending on the number of assets."""
                header += "," + str(self.NumberOfAssets - n) + " Avail."
            """The field names for the CSV file."""
            csv = "Algorithm,Data,Weight,Sort,Manhours,Grounded Days,Ground Raw Count," + \
                  "Grounding Events,Inefficiencies,Scheduled,Violations,Optimal,Average," + \
                  "Usage Viol.,Imminent Usg., Midterm Usg., Planned Usg.,Extended Grnd" + \
                  header + "\n"
        else: csv = ""
        """Write out to the file and close."""    
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
               str(self.Midterm)                    + "," + \
               str(self.UsageTotal)                 + "," + \
               str(self.ExtendedGround)             + \
               self.availability()                  + "\n"
        fo.write(csv)
        fo.close()