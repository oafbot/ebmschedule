from datetime import datetime
from datetime import timedelta
from outputs.Output import Output
# from abc import ABCMeta

class Algorithm:
    """Parent class for algorithms"""
    # __metaclass__ = ABCMeta
    
    def __init__(self, input, weight=1.0, name="Algorithm", relax=0):
        self.name       = name
        self.weight     = weight # 0 <= weight <= 1
        self.totalTasks = len(input.tasks)
        self.conflicts  = 0
        self.prev       = 0
        self.output     = Output(input)
        self.stopwatch  = datetime.now()
        self.processed  = {}
        self.relax      = relax
        
        if(input.trace): 
            self.output.console()
        if(input.conf.pushcal): 
            self.calendar(input)        
        for asset in input.assets:
            self.processed[asset.id] = set()
        
        self.sort(input)        
        self.main(input)
        
    def sort(self, input):
        """
        Prioritize the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex ( i.e. conflict heavy ) task first.
        """
        input.tasks.sort(key=lambda task: 
            (     
                (self.weight * ((task.manhours / (task.totalAvailableHours *1.0)) 
                if task.totalAvailableHours else 0)) + 
                ((1-self.weight) * (len(task.conflicts) / (self.totalTasks *1.0)))
                ), reverse=True
            )
    
    def main(self, input):
        for task in input.tasks:
            for asset in input.assets:
                if(task.interval):
                    """
                    If the task is to be performed at a set interval,
                    Set the new start date to the later of either:
                      A. The last time a task was performed on a given asset
                      B. The start date of the given date range.
                    """ 
                    start = task.next(asset, input.schedule.last(asset, task))
                    start = max(start, input.schedule.dateRange.start)
                    bundle = task.checkConstraints(list(), asset, input)
                    if len(bundle) > 1:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    else:
                        self.regularSchedule(asset, task, input, start)
                # input.schedule.processed.clear()
        self.analytics(input)
        self.results = input
                
    def console(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""
        self.output.printSchedule(self, asset, task, start, end) 
    
    def analytics(self, input):
        """Print out the cost analysis for the algorithm."""
        print "\n", \
              self.name + ":", input.schedule.dataSource, input.count, \
              "    Manhours:", input.schedule.totalManhours, \
              "    Adjustments:", self.conflicts
        print "\nExecution:", str(datetime.now()-self.stopwatch)[:-4]
        
        """Write out metrics to a file."""
        if(input.conf.metrics):
            self.output.writeMetrics(input, self.conflicts)
    
    def calendar(self, input):
        """Initiate the Google Calendar."""
        from outputs.Calendar import Calendar        
        if not input.schedule.cal: 
            input.schedule.cal = Calendar()
        input.schedule.cal.Connect(input)