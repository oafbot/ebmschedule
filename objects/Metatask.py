from Task import Task

class Metatask(Task):
    def __init__(self, tasks):
        
        Task.__init__(self, id, name, workhours, threshold, interval, manpowers, conflicts=list()):