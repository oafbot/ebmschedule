#!/usr/local/bin/python
import subprocess
import sys
import argparse
from datetime import datetime
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='crunch')
    parser.add_argument('--start', type=int, help='Load initial conditions starting with this dataset.')
    parser.add_argument('--end',   type=int, help='Last dataset of initial conditions to load.')
    parser.add_argument('--algo',  type=int, help='The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft')
    parser.add_argument('--sort',  type=str, help='Turn sorting on, off, or reverse')
    args = vars(parser.parse_args())

    algo  = args['algo' ] if args['algo' ] is not None else 0
    start = args['start'] if args['start'] is not None else 0
    end   = args['end'  ] if args['end'  ] is not None else 0
    sort  = args['sort' ] if args['sort' ] is not None else 'on'
    lax   = 5 if algo == 1 else 2

    # weights = [0, 5, 10] if algo != 2 else [0]
    weights = [0, 2, 4, 6, 8, 10] if algo != 2 else [0]
    count = 0
    runs  = len(range(start, end+1)) * len(weights) * len(range(1, lax)) 
    timer = datetime.now()

    for data in range(start, end+1):
        """Load initial condition dataset corresponding to data."""
        for weight in weights:
            """Vary weight from 0 to 1.0. Increment by 0.5."""
            for relax in range(1, lax):
                """Vary the relaxing 25 percent to (lax-1)*25 percent."""
                count += 1
                print "Running", count, "out of", runs
                subprocess.call(["../main.py", str(algo), str(data), str(weight), str(relax)])

    print "Executed", runs, "runs in", str(datetime.now()-timer)[:-4] + "\a\n"
