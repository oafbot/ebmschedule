#!/usr/local/bin/python
import subprocess
import sys
import argparse
# ================================================================
# = Run Diffs on the outputs of two runs.                        =
# ================================================================

# USAGE: 
# ./diffs.py --left 1-0-2-2 --right 1-0-4-2
# ./diffs.py --left 1-0-0-1 --right 1-0-0-1 --plat 2 --sortL on --sortR off

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='crunch')
    parser.add_argument('--left',  type=str, help='Left side of diff.')
    parser.add_argument('--right', type=str, help='Right side of diff.')
    parser.add_argument('--trace', action="store_true", default=False, help='Trace data on console.')
    parser.add_argument('--sortL',  type=str, help='Turn sorting on, off, or reverse for left')
    parser.add_argument('--sortR',  type=str, help='Turn sorting on, off, or reverse for right')
    parser.add_argument('--plat',  type=str, help='The platform to run the algorithm on.')
        
    args = vars(parser.parse_args())    
    arg1 = args['left'].split("-")
    arg2 = args['right'].split("-")
    trace = '1' if args['trace'] is True else '0'
    sort1 = args['sortL'] if args['sortL'] is not None else 'on'
    sort2 = args['sortR'] if args['sortR'] is not None else 'on'
    plat  = args['plat']  if args['plat' ] is not None else '1' 
    
    
    if   sort1 == "on":      sorting1 = "+"
    elif sort1 == "off":     sorting1 = "-"
    elif sort1 == "reverse": sorting1 = "!"
    
    if   sort2 == "on":      sorting2 = "+"
    elif sort2 == "off":     sorting2 = "-"
    elif sort2 == "reverse": sorting2 = "!"
            
    algo1   = arg1[0]
    data1   = arg1[1]
    weight1 = arg1[2]
    relax1  = arg1[3]
    
    algo2   = arg2[0]
    data2   = arg2[1]
    weight2 = arg2[2]
    relax2  = arg2[3]
    
    f = open("../tests/diff1.txt", "w")
    subprocess.call(["../main.py", algo1, data1, weight1, relax1, sorting1, plat, trace], stdout=f)
    f.close()
    f = open("../tests/diff2.txt", "w")
    subprocess.call(["../main.py", algo2, data2, weight2, relax2, sorting2, plat, trace], stdout=f)
    f.close()
    subprocess.call(["/usr/bin/opendiff", "../tests/diff1.txt", "../tests/diff2.txt"])