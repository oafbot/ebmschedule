#!/usr/local/bin/python
import subprocess
import shlex
import sys
from datetime import datetime
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

if __name__ == "__main__":
    timer = datetime.now()
    
    """Handle command line args."""
    plat  = "--plat "  + sys.argv[1] if len(sys.argv)>1 else "--plat 1"
    batch = "--batch " + sys.argv[2] if len(sys.argv)>2 else "--batch 0"
    trace = "--trace" if len(sys.argv)>3 and sys.argv[3] == '+' else ""
                
    start = "--start 0"
    end   = "--end 9"
    algos = ["--algo 0", "--algo 1", "--algo 2"]
    sorts = ["--sort on", "--sort off", "--sort reverse"]
    
    stages = len(algos) * len(sorts)
    count = 0
     
    for sort in sorts:
        for algo in algos:
            count += 1
            status = "Stage " + str(count) + " of " + str(stages) + " "
            print "\n" + status + "-" * (110 - len(status))
            command = "./crunch.py %s %s %s %s %s %s %s" % (algo, start, end, sort, batch, plat, trace)
            subprocess.call(shlex.split(command))

    print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"
