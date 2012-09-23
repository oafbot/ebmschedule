from datetime import timedelta
from datetime import datetime
class Tests:
    def __init__(self, model):
        self.schedule = model.schedule
        self.tasks = model.tasks
        self.assets = model.assets
        scheduled = self.schedule._scheduledTasks
        
        for asset in self.assets:            
            print "\nAsset:", asset.name
            print "-------------------------------------------"
            dates = scheduled[asset.id].keys() 
            dates.sort(key=lambda d: (d.year, d.month, d.day))
            
            previous_date = None
            previous_task = None
            for date in dates:
                for task in model.tasks:
                    if task.id in scheduled[asset.id][date]:
                        """If the task is in the schedule for that day."""
                        if(previous_date == None):
                            previous_date = date
                        elif(prev < asset.start and date > prev):
                            previous_date = date
                        elif(date >= asset.start and task.interval > 0): 
                            """If the date is later than start date and the interval is not zero."""
                            difference = date - prev
                            if(difference != timedelta(days=task.interval)):
                                """If the difference is not the same as the interval."""
                                print "Violation"
                                print "Task: " + str(task.id), task.name 
                                print "Date:", str(date)[:-9]
                                print "Last:", str(prev)[:-9]
                                # print "Interval:", str(timedelta(days=task.interval))[:-9]
                                print "Interval:", self.strfdelta(timedelta(days=task.interval), "{days} days")
                                print "Difference:", self.strfdelta(difference, "{days} days")
                                print "-------------------------------------------"
                            previous_date = date
                            previous_task = task.id

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)