class Model:
    
    def __init__(self):        
        from datetime import datetime
        import time
        from objects import Asset, Skill, Manpower
        from objects.Schedule import Schedule
        from objects.Task import Task
        from objects.DateRange import DateRange
                
        self.name = "Simple-Model"
        
        self.trace   = False
        self.bigdata = False
        
        self.now   = time.gmtime()
        self.year  = self.now.tm_year
        self.month = self.now.tm_mon
        self.day   = self.now.tm_mday
                
        self.endy  = self.year  + 0
        self.endm  = self.month + 1
        self.endd  = self.day   + 0
        
        self.start = datetime(self.year, self.month, 1)
        self.end   = datetime(self.endy, self.endm, 10)
        
        #---------------------------------------------------------------------------
        
        
        schedule = Schedule(self.name, DateRange(self.start, self.end), 2)
        
        assets = {
            1: Asset(1, 'E-6B 01', self.start),
            2: Asset(2, 'E-6B 02', self.start),
            3: Asset(3, 'E-6B 03', self.start)
        }

        skills = {
            1: Skill(1, 'Electrician', 5, 8),
            2: Skill(2, 'Mechanic', 10, 8),
            3: Skill(3, 'Painter', 1, 8),
            4: Skill(4, 'Misc. Ground Crew', 15, 8)
        }
        
        tasks = {
            1: Task(
                id=1, 
                name='Change Oil', 
                unit=1, 
                threshold=5, 
                interval=14, 
                manpowers=[
                    Manpower(1, skills[1], 1),
                    Manpower(2, skills[2], 4),
                    Manpower(3, skills[2], 2)
                ], 
                conflicts=[2,4],
                prep   = [],
                prereq = [],
                subseq = [],
                concur = [8]
            ),
            2: Task(
                id=2, 
                name='Paint',
                unit=1, 
                threshold=20,
                interval=30, 
                manpowers=[
                    Manpower(4, skills[3], 20)
                ], 
                conflicts=[1,3,4,5,6,7,8,9],
                prep   = [],
                prereq = [7],
                subseq = [],
                concur = []
            ),
            3: Task(
                id=3,
                name='Pitot probe',
                unit=1,
                threshold=8,
                interval=20,
                manpowers=[
                    Manpower(5, skills[1], 2),
                    Manpower(6, skills[2], 4)
                ], 
                conflicts=[2,7],
                prep   = [],
                prereq = [],
                subseq = [],
                concur = []
            ),
            4: Task(
              id=4, 
              name='Engine Assembly', 
              unit=1, 
              threshold=10, 
              interval=40, 
              manpowers=[
                  Manpower(7, skills[1], 9),
                  Manpower(8, skills[2], 30)
              ], 
              conflicts=[1,2,7],
              prep   = [5],
              prereq = [],
              subseq = [6],
              concur = []
            ),
            5: Task(
              id=5, 
              name='Remove Panel', 
              unit=1, 
              threshold=0, 
              interval=0, 
              manpowers=[
                  Manpower(9, skills[2], 1)
              ], 
              conflicts=[2,7],
              prep   = [9],
              prereq = [],
              subseq = [],
              concur = []
            ),
            6: Task(
              id=6, 
              name='Add Panel', 
              unit=1, 
              threshold=0, 
              interval=0, 
              manpowers=[
                  Manpower(9, skills[2], 1)
              ], 
              conflicts=[2,7],
              prep   = [],
              prereq = [],
              subseq = [],
              concur = []
            ),
            7: Task(
              id=7, 
              name='Wash', 
              unit=1, 
              threshold=0, 
              interval=7, 
              manpowers=[
                  Manpower(10, skills[4], 5),
                  Manpower(11, skills[4], 5),
                  Manpower(12, skills[4], 5)
              ], 
              conflicts=[1,2,3,4,5,6,8,9],
              prep   = [],
              prereq = [],
              subseq = [],
              concur = []
            ),
            8: Task(
              id=8, 
              name='Replace Filter', 
              unit=1, 
              threshold=0, 
              interval=21, 
              manpowers=[
                  Manpower(13, skills[2], 1)
              ], 
              conflicts=[2,7],
              prep   = [],
              prereq = [],
              subseq = [],
              concur = [1]
            ),
            9: Task(
              id=9, 
              name='Dismantle Bulkhead', 
              unit=1, 
              threshold=0, 
              interval=0, 
              manpowers=[
                  Manpower(14, skills[2], 2)
              ], 
              conflicts=[2,7],
              prep   = [],
              prereq = [],
              subseq = [],
              concur = []
            ),
        }
        
        
        # import random
        # for i, asset in enumerate(assets):
        #     for task in tasks:
        #         date = datetime(2012, 7, random.randrange(1, 30))
        #         schedule.force(assets[asset], tasks[task], DateRange(date, date))
        # 
        # ---------------------------------------------------------------------------
        
        # schedule.force(assets[1], tasks[7], 
        #             DateRange(datetime(2012, 8, 15), datetime(2012, 8, 15)))
        
        # schedule.force(assets[1], tasks[2], 
        #     DateRange(datetime(2012, 1, 1), datetime(2012, 1, 1)))
        # 
        # schedule.force(assets[2], tasks[1], 
        #     DateRange(datetime(2012, 1, 1), datetime(2012, 1, 1)))
        # 
        # schedule.force(assets[2], tasks[2], 
        #     DateRange(datetime(2012, 1, 1), datetime(2012, 1, 1)))
        # 
        # schedule.force(assets[3], tasks[1], 
        #     DateRange(datetime(2012, 1, 1), datetime(2012, 1, 1)))
        # 
        # schedule.force(assets[3], tasks[2], 
        #     DateRange(datetime(2012, 1, 1), datetime(2012, 1, 1)))


        self.assets = assets.values()
        self.tasks = tasks.values()
        self.skills = skills.values()
        self.schedule = schedule