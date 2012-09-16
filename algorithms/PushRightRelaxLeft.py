from datetime import timedelta
import main

class PushRightRelaxLeft:
    
    def __init__(self, input):
        weight = 1.0 # 0 <= weight <= 1
        totalTasks = len(input.tasks)
        self.conflicts = 0
        self.prev = 0
        self.name = "PushRight-RelaxLeft"
        self.RELAX = -3
        self.schedule = input.schedule
        
        """
        Prioritize the tasks that require higher percentage of resources.
        How many of the skills for the task are available.
        Divide manhours cost with total available manhours.
        Schedule the complex ( i.e. conflict heavy ) task first.
        """
        input.tasks.sort(key=lambda task:
            (
                (weight * ((task.manhours / (task.totalAvailableHours *1.0))
                if task.totalAvailableHours else 0)) + 
                ((1-weight) * (len(task.conflicts) / (totalTasks *1.0)))
            ),
            reverse=True)
        
        if(input.conf.pushcal):
            self.initcal(input)
                
        for asset in input.assets:
            for task in input.tasks:
                if(task.interval):
                    """
                    If the task is to be performed at a set interval,
                    Set the new start date to the later of either:
                      A. The last time a task was performed on a given asset
                      B. The start date of the given date range.
                    """                    
                    start = task.next(asset, self.schedule.last(asset, task))
                    start = max(start, self.schedule.dateRange.start)
                    bundle = task.checkConstraints(list(), asset, input)
                    if len(bundle) > 1:
                        self.bundleSchedule(bundle, asset, input, task, start)
                    else:
                        self.regularSchedule(asset, task, input, start)
            self.schedule.processed = []
        # input.schedule.cal.PushBatchRequest()
        self.analytics(input)

    def regularSchedule(self, asset, task, input, start):
        """
        Schedule single tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        """
        oInterval = task.interval
        oStart = start
        while(start <= input.schedule.dateRange.end):
            n = 0 
            start = self.shift(asset, task, start, oInterval, oStart, n)
            task.interval = oInterval
            end = input.schedule.add(asset, task, start)
            self.output(asset, task, input, start, end)
            start = task.next(asset, end)

    def bundleSchedule(self, bundle, asset, input, task, start):
        """
        Schedule bundled tasks.
        While the start date is within the date range,
        Keep Shifting one day forward as long as a schedule conflict exists.
        Check against the length of the entire bundle of tasks.
        Schedule individual tasks in consecutive order once an empty slot is found.
        """
        metatask = task.bundleAsTask(bundle, asset)
        oInterval = metatask.interval
        oStart = start
        while(start <= input.schedule.dateRange.end):
            n = 0
            start = self.shift(asset, metatask, start, oInterval, oStart, n)
            metatask.interval = oInterval
            remainder_hours = 0            # The hours carried over from the preceding task
            maxhours = task.hoursPerDay    # The work hours in a day
            longest = 0                    # The task that takes the longest to perform
            
            """For each task in the bundle, schedule in order."""
            for bundle_task in bundle:
                overhours  = False
                if not bundle_task.withinInterval(input.schedule, asset, start):
                    end = input.schedule.add(asset, bundle_task, start)
                
                    self.output(asset, bundle_task, input, start, end)
                
                    """Find the the most costly task."""
                    for manpower in bundle_task.manpowers:
                        if manpower.hours > longest: longest = manpower.hours
                
                    """If the task takes takes longer than the workday, carry over."""
                    if longest <= maxhours:
                        hours = longest
                        if hours + remainder_hours >= maxhours: overhours = True
                    else: hours = longest % maxhours
                
                    """Determine the hours remaining on a task that need to be carried over."""
                    if hours + remainder_hours == maxhours:
                        remainder_hours = 0
                    elif hours + remainder_hours > maxhours:
                        remainder_hours = (remainder_hours + hours) - maxhours
                    else:
                        remainder_hours += hours
                
                    """Set the start date. Push to next day if overtime."""
                    if overhours: start = end + timedelta(days=1)
                    else: start = end
                else: end = start
                # input.schedule.processed.append(bundle_task.id)
            start = task.next(asset, end)
    
    def shift(self, asset, task, start, interval, ostart, n):
        while(self.schedule.blocked(asset, task, start)):
            if n > self.RELAX:
                task.interval = interval + self.RELAX
                if start - timedelta(days=1) >= asset.start:
                    start -= timedelta(days=1)
                    n -= 1
                    self.conflicts += 1
                else: break
            else:
                if start < ostart:
                    start = ostart
                task.interval = interval
                start += timedelta(days=1)
                self.conflicts += 1
        return start
    
    def output(self, asset, task, input, start, end):
        """Print out the scheduling output to the console."""
        main.outputs.output.printSchedule(self, asset, task, start, end)

    def analytics(self,input):
        """Print out the cost analysis for the algorithm."""
        print "\n",                                                                            \
              self.name+":", input.schedule.dataSource,                                        \
              "Manhours:", input.schedule.totalManhours,                                       \
              " Counts:", self.conflicts
        
        """Write out metrics to a file."""
        if(input.conf.metrics):
            main.outputs.output.writeMetrics(input, self.conflicts)
    
    def initcal(self, input):
        from outputs.Calendar import Calendar
        import gdata.service
        import time
        
        count = 0
        colors = ['#A32929', '#B1365F',	'#7A367A', '#5229A3', '#29527A', '#2952A3', '#1B887A', '#28754E', 
                  '#0D7813', '#528800', '#88880E', '#AB8B00', '#BE6D00', '#B1440E', '#865A5A', '#705770', 
                  '#4E5D6C', '#5A6986', '#4A716C', '#6E6E41', '#8D6F47', '#853104', '#691426', '#5C1158', 
                  '#23164E', '#182C57', '#060D5E', '#125A12', '#2F6213', '#2F6309', '#5F6B02', '#8C500B', 
                  '#8C500B', '#754916', '#6B3304', '#5B123B', '#42104A', '#113F47', '#333333', '#0F4B38', 
                  '#856508', '#711616']
        trying = True
        attempts = 0
        sleep_secs = 1
        gsessionid = ''

        if not input.schedule.cal: input.schedule.cal = Calendar()
        
        print "Purging calendar."          
        input.schedule.cal.DeleteAll()
        print "..."
        
        for asset in input.assets:
            while trying:
                trying = False
                attempts += 1
                try:
                    input.schedule.cal.NewCalendar(asset.name, asset.name, 'E-6B', colors[count])
                except gdata.service.RequestError as inst:
                    thing = inst[0]
                    if thing['status'] == 302 and attempts < 8:
                        trying = True
                        gsessionid=thing['body'][ thing['body'].find('?') : thing['body'].find('">here</A>')]
                        print 'Received redirect - retrying in', sleep_secs, 'seconds with', gsessionid
                        time.sleep(sleep_secs)
                        sleep_secs *= 2
                    else:
                        print 'too many RequestErrors, giving up'
            if(count < len(colors)):
                count += 1
            else:
                count = 0