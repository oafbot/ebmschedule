#!/usr/bin/python
import subprocess
import sys
import argparse
# ================================================================
# = Automated runs of the EBM Scheduler with variable conditions =
# ================================================================

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='crunch')
    parser.add_argument('--start', type=int, help='Load initial conditions starting with this dataset.')
    parser.add_argument('--end',   type=int, help='Last dataset of initial conditions to load.')
    parser.add_argument('--algo',  type=int, help='The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft')
    args = vars(parser.parse_args())    

    algo  = args['algo' ] if args['algo' ] else 0
    start = args['start'] if args['start'] else 0
    end   = args['end'  ] if args['end'  ] else 10
    lax   = 9 if algo > 0 else 2
    
    for data in range(start, end):
        """Load initial condition dataset corresponding to i."""
        for weight in range(0, 11):
            """Vary weight from 0 to 1.0. Increment by 0.1."""
            for relax in range(1, lax):
                """Vary the relaxing ten to fifty percent."""
                subprocess.call(["../main.py", str(algo), str(data), str(weight), str(relax)])