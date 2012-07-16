from random import randint 

schedule_window_min = 30
schedule_window_max = 45
schedule_assets_min = 5
schedule_assets_max = 10

asset_total_min = 5
asset_total_max = 10
asset_year_min = 1998
asset_year_max = 2009
asset_month_min = 1
asset_month_max = 12
asset_day_min = 1
asset_day_max = 27

skill_total_min = 5
skill_total_max = 10
skill_available_min = 1
skill_available_max = 20
skill_hoursPerDay_min = 8
skill_hoursPerDay_max = 8

task_total_min = 5
task_total_max = 10
task_unit_min = 1
task_unit_max = 1
task_threshold_min = 0
task_threshold_max = 20
task_interval_min = 5
task_interval_max = 30

manpower_total_min = 1
manpower_total_max = 6
manpower_hours_min = 1
manpower_hours_max = 6

conflict_total_min = 0
conflict_total_max = 5

initial_total_min = 10
initial_total_max = 20
initial_year_min = 1998
initial_year_max = 2009
initial_month_min = 1
initial_month_max = 12
initial_day_min = 1
initial_day_max = 27


f = open('Random.py', 'w')
f.write("class Random:\n")
f.write("    def __init__(self):\n")
f.write("        from datetime import datetime\n")
f.write("        from datetime import timedelta\n")
f.write("        from objects import Asset, Skill, Manpower\n")
f.write("        from objects.Schedule import Schedule\n")
f.write("        from objects.Task import Task\n")
f.write("        from objects.DateRange import DateRange\n")
f.write("        self.name = 'Random'\n")
f.write("        _now = datetime.now()\n")
f.write("        _window = "+str(randint(schedule_window_min, schedule_window_max))+"\n")
f.write("        _maxAssetsInWork = "+str(randint(schedule_assets_min, schedule_assets_max))+"\n")
f.write("        schedule = Schedule(self.name, DateRange(_now, _now + timedelta(days=_window)), _maxAssetsInWork)\n")

f.write("        assets = {\n")

asset_total = randint(asset_total_min, asset_total_max)
for x in range(1, asset_total+1):
    asset = "            "+str(x)+": Asset("+str(x)+", 'Asset "+str(x)+"', datetime("+str(randint(asset_year_min,asset_year_max))+", "+str(randint(asset_month_min,asset_month_max))+", "+str(randint(asset_day_min,asset_day_max))+"))"
    if x != asset_total: asset+= ","
    asset += "\n"
    f.write(asset)    

f.write("        }\n")

f.write("        skills = {\n")
skill_total = randint(skill_total_min, skill_total_max)
for x in range(1, skill_total+1):
    skill = "            "+str(x)+": Skill("+str(x)+", 'Skill "+str(x)+"', "+str(randint(skill_available_min,skill_available_max))+", "+str(randint(skill_hoursPerDay_min,skill_hoursPerDay_max))+")"
    if x != skill_total: skill+= ","
    skill += "\n"
    f.write(skill)    
f.write("        }\n")

f.write("        tasks = {\n")

task_total = randint(task_total_min, task_total_max)
for x in range(1, task_total+1):
    task = "            "+str(x)+": Task(\n"
    task += "                id="+str(x)+", \n"
    task += "                name='Task "+str(x)+"', \n"
    task += "                unit="+str(randint(task_unit_min,task_unit_max))+", \n"
    task += "                threshold="+str(randint(task_threshold_min,task_threshold_max))+", \n"
    task += "                interval="+str(randint(task_interval_min,task_interval_max))+", \n"
    task += "                manpowers=[\n"
    
    manpower_total = randint(manpower_total_min, manpower_total_max)
    for y in range(1, manpower_total+1):
        manpower = "                    Manpower("+str(y)+", skills["+str(randint(1,skill_total))+"], "+str(randint(manpower_hours_min,manpower_hours_max))+")"
        if y != manpower_total: manpower+= ","
        manpower += "\n"    
        task += manpower
    
    task += "                ], \n"

    task += "                conflicts=["
    conflict_total = randint(conflict_total_min, conflict_total_max)
    for y in range(1, conflict_total+1):
        conflict = str(randint(1,task_total))
        if y != conflict_total: conflict+= ", "
        task += conflict
    task += "], \n"
    task += "                totalTasks="+str(task_total)+" \n"

    task += "            )"

    if x != task_total: task+= ","
    task += "\n"
    f.write(task)    

f.write("        }\n")

for x in range(randint(initial_total_min, initial_total_max)):
    schedule = "datetime("+str(randint(initial_year_min,initial_year_max))+", "+str(randint(initial_month_min,initial_month_max))+", "+str(randint(initial_day_min,initial_day_max))+")"
    f.write("        schedule.force(assets["+str(randint(1,asset_total))+"], tasks["+str(randint(1,task_total))+"], DateRange("+schedule+", "+schedule+"))\n")
    
f.write("        self.assets = assets.values()\n")
f.write("        self.tasks = tasks.values()  \n")      
f.write("        self.schedule = schedule\n")
f.close()

print "done"