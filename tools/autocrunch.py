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
    batch = "--batch " + sys.argv[1] if len(sys.argv)>1 else "--batch 0"
            
    start = "--start 0"
    end   = "--end 9"
    algos = ["--algo 0", "--algo 1"]
    sorts = ["--sort on", "--sort off", "--sort reverse"]
     
    for sort in sorts:
        for algo in algos:
            command = "./crunch.py %s %s %s %s %s" % (algo, start, end, sort, batch)
            subprocess.call(shlex.split(command))

    print "Executed in", str(datetime.now()-timer)[:-4] + "\a\n"
