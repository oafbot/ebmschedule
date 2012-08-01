class PushToRight:
    
    def __init__(self, input):
        #from datetime import timedelta
        weight = 1.0 # 0 <= weight <= 1
        totalTasks = len(input.tasks)
        self.conflicts = 0
        prev = 0
        
        """
        Prioritze the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex ( i.e. conflict heavy ) task first.
        """
        input.tasks.sort(key=lambda task: 
            (     
                (weight * ((task.manhours / (task.totalAvailableHours *1.0)) 
                 if task.totalAvailableHours else 0)) 
                + ((1-weight) * (len(task.conflicts) / (totalTasks *1.0)))
             ), 
            reverse=True)
        
        for asset in input.assets:        
            for task in input.tasks:
                if(task.interval):
                    """ 
                    If the task is to be performed at a set interval,
                    Set the new start date to the later of either:
                      A. The last time a task was performed on a given asset
                      B. The start date of the given date range.
                    """
                    bundle = task.checkConstraints(bundle = [])
                    if len(bundle) > 1:
                        self.bundleSchedule(bundle, asset, prev)
                    else:
                        self.regularSchedule(asset, task, input, prev)
                    
                    #if len(bundle) > 1:
                    #    for task in bundle: print "--------------  ", task.name
                    #task.reset()
        print "\n",                                                                            \
              "PushToRight", input.schedule.dataSource,                                        \
              "Manhours:", input.schedule.totalManhours,                                       \
              " Counts:", self.conflicts


    def regularSchedule(self,asset,task,input,prev):
        from datetime import timedelta
        start = task.next(asset, input.schedule.last(asset, task))
        start = max(start, input.schedule.dateRange.start)
        
        while(start <= input.schedule.dateRange.end):
            while(input.schedule.blocked(asset, task, start)):
                """
                While the start date is within the date range,
                Keep Shifting one day forward as long as a schedule conflict exists.
                """ 
                start += timedelta(days=1) # Shift to the right one day when blocked
                self.conflicts += 1
            end = input.schedule.add(asset, task, start) # Add to schedule

            if input.name == "iSUMO":
                print str.ljust(asset.name, 8), str.ljust(task.name, 112),         \
                      str.ljust(str(start)[:-16], 10), "--",                       \
                      str.ljust(str(end)[:-16], 10)
            elif input.name == "iSUMOe6Random":
                print str.ljust(asset.name, 8), str.ljust(task.name, 112),         \
                      str.ljust(str(start)[:-9], 10), "--",                        \
                      str.ljust(str(end)[:-9], 10)
            else:
                if prev != asset.name: print ""
                print str.ljust(asset.name, 16),                                   \
                      str.ljust(task.name, 16),                                    \
                      str.ljust(str.replace(str(start), "00:00:00", ""), 10), "--",\
                      str.ljust(str.replace(str(end), "00:00:00", ""), 10)
                prev = asset.name
            
            start = task.next(asset, end)
    
    def bundleSchedule(self, bundle, asset, prev):
        for task in bundle:
           if prev != asset.name: print ""
           print str.ljust(asset.name, 16),                                   \
                 str.ljust(task.name, 16)#,                                   \
                 #str.ljust(str.replace(str(start), "00:00:00", ""), 10), "--",\
                 #str.ljust(str.replace(str(end), "00:00:00", ""), 10)
           prev = asset.name
            
            
            
                # TODO: 
                # No Maintenance Period
                # planned usage
                # task start/end dates
                # number per a year FY
                # configuration
                # pre/post/conflicting tasks
                # pre tasks
                # schedule precision
                # order tasks by largest size / availability