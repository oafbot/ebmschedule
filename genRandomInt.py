from datetime import date
from datetime import timedelta
from random import randint

#Select which input file to randomize initial conditions
from inputs.iSUMOe6Random import iSUMOe6Random
d = iSUMOe6Random()
ranInputsToGenerate = 10

inputFile = d.name

#generate new inputs
for fileNum in range(ranInputsToGenerate):

    fileLocation = 'inputs/' + inputFile + '.py'
    source = open(fileLocation, 'r')
    newInput = inputFile + str(fileNum+1)
    newFile = 'inputs/' + newInput + '.py'
    f = open(newFile, 'w')
    
    line = source.readline()
     
    while line:
        lineNoSpace = line.strip()
        if lineNoSpace.startswith('self.assets'): break
        if lineNoSpace.startswith('class'): f.write('class '+newInput+':\n')
        elif lineNoSpace.startswith('self.name'): f.write('\t\tself.name = "'+newInput+'"\n')
        elif not lineNoSpace.startswith('schedule.force'): f.write(line)
        line = source.readline()
    
    for t in d.tasks:
        if t.interval:
            for a in d.assets:
                schedule = d.schedule.dateRange.start - timedelta(days=randint(0,t.interval)) #random date
                schedule = "datetime("+str(schedule.year)+", "+str(schedule.month)+", "+str(schedule.day)+")"
                f.write("\t\tschedule.force(assets["+str(a.id)+"], tasks["+str(t.id)+"], DateRange("+schedule+", "+schedule+"))\n")
    
    while line:
        f.write(line)
        line = source.readline()
    
    source.close()
    f.close()
    
#wire in new inputs
f = open('inputs/__init__.py', 'w')
for fileNum in range(ranInputsToGenerate):
    newInput = inputFile + str(fileNum+1)
    f.write('from '+newInput+' import '+newInput+'\n')
    
f.write('\ninputs = [')

for fileNum in range(ranInputsToGenerate):
    newInput = inputFile + str(fileNum+1)
    f.write(newInput+'(),')
    
f.write(']\n')

f.close()    

print "done"