#!/usr/local/bin/python
import subprocess
import sys
import argparse
# ================================================================
# = Run Diffs on the outputs of two runs.                        =
# ================================================================

# USAGE: ./diffs.py --left 1-0-2-2 --right 1-0-4-2

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='crunch')
    parser.add_argument('--left',  type=str, help='Left side of diff.')
    parser.add_argument('--right', type=str, help='Right side of diff.')
    parser.add_argument('--trace', action="store_true", default=False, help='Trace data on console.')
    parser.add_argument('--sort',  type=str, help='Turn sorting on, off, or reverse')
    parser.add_argument('--plat',  type=int, help='The platform to run the algorithm on.')
        
    args = vars(parser.parse_args())    
    arg1 = args['left'].split("-")
    arg2 = args['right'].split("-")
    trace = '1' if args['trace'] is True else '0'
    sort  = args['sort' ] if args['sort' ] is not None else 'on'
    plat  = args['plat' ] if args['plat' ] is not None else '1' 

    if   sort == "on":      sorting = "+"
    elif sort == "off":     sorting = "-"
    elif sort == "reverse": sorting = "!"
            
    algo1   = arg1[0]
    data1   = arg1[1]
    weight1 = arg1[2]
    relax1  = arg1[3]
    
    algo2   = arg2[0]
    data2   = arg2[1]
    weight2 = arg2[2]
    relax2  = arg2[3]
    
    f = open("../tests/diff1.txt", "w")
    subprocess.call(["../main.py", algo1, data1, weight1, relax1, sorting, plat, trace], stdout=f)
    f.close()
    f = open("../tests/diff2.txt", "w")
    subprocess.call(["../main.py", algo2, data2, weight2, relax2, sorting, plat, trace], stdout=f)
    f.close()
    subprocess.call(["/usr/bin/opendiff", "../tests/diff1.txt", "../tests/diff2.txt"])