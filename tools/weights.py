#!/usr/local/bin/python
import subprocess
import sys
import argparse
from datetime import datetime, timedelta
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='crunch')
    parser.add_argument('--start', type=int, help='Load initial conditions starting with this dataset.')
    parser.add_argument('--end',   type=int, help='Last dataset of initial conditions to load.')
    parser.add_argument('--algo',  type=int, help='The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft')
    parser.add_argument('--lax',   type=int, help='The relax factors to use.')
    parser.add_argument('--plat',  type=int, help='The platform to run the algorithm on.')
    parser.add_argument('--trace', action="store_true", default=False, help='Trace data on console.')
    
    args = vars(parser.parse_args())

    algo  = args['algo' ] if args['algo' ] is not None else 0
    start = args['start'] if args['start'] is not None else 0
    end   = args['end'  ] if args['end'  ] is not None else 0
    lax   = args['lax'  ] if args['lax'  ] is not None else 5
    plat  = args['plat' ] if args['plat' ] is not None else 1    
    trace = 1 if args['trace'] is True else 0
    lax   = 1 + lax / 25 if algo == 1 else 2
    sort  = 'on'
    
    weights = [0, 2, 4, 6, 8, 10]
    count = 0
    runs  = len(range(0, 1)) * len(range(start, end+1)) * len(weights) * len(range(1, lax))
    timer = datetime.now()
    
    if   sort == "on":      sorting = "+"
    elif sort == "reverse": sorting = "!"
    
    print "\nEstimated execution time:", str(runs/60) + ":", "\b" + \
           str(runs%60) if runs%60 > 9 else "\b0" + str(runs%60), "hours", \
           "\tCheck back", str(timer + timedelta(seconds=runs*60))[:-7]
    
    for proc in range(0, 1):
        """Load xml file with the matching number."""
        for data in range(start, end+1):
            """Load initial condition dataset corresponding to data."""
            for relax in range(1, lax):
                """Vary the relaxing 25 percent to (lax-1)*25 percent."""
                for weight in weights:
                    """Vary weight from 0 to 1.0. Increment by 0.5."""
                    count += 1
                    status = "Running " + str(count) + " out of " + str(runs) + " "
                    print status + "-" * (110-len(status))
                    subprocess.call(["../main.py", str(algo), str(data), str(weight), str(relax), 
                                    sorting, str(plat), str(trace), str(proc)])

    print "Executed", runs, "runs in", str(datetime.now()-timer)[:-4] + "\a\n"
