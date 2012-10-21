EBM Scheduler
=============
## Algorithms
#### PushToRight:
If there are conflicts on the scheduled day, try to schedule by pushing one day forward.
#### PushRight-RelaxLeft:
If there are conflicts on the scheduled day, push one day back as long as a conflict exists until predetermined floor is reached. 
If task was not scheduled try pushing forward until ceiling is reached.

## Main
#### Usage:
	$ ./main.py [algorithm] [data] [weight] [relax]
	
#### Example:
	$ ./main.py 1 0 5 3
	
* ***Algorithm*** is the algorithm to use. 0 is PushRight, 1 is PushRight-RelaxLeft.
* ***Data*** is the initial conditions to load. Ranges from 0 to as many datasets as was generated.
* ***Weight*** is the weight applied to sorting algorithm. Ranges from 0 to 10 (represents 0.0 to 1.0)
* ***Relax*** is the percentage of interval to relax left. Ranges from 1 to 9 (represents 10% to 90%)

## Tools
### crunch.py
Run main.py N number of times with varying weights and relaxing (if relax left algorithm).

#### Usage: 
	$ ./crunch.py [-h] [--start START] [--end END] [--algo ALGO]
#### Example:
	$ ./crunch.py --algo 1 --start 0 --end 1 

#### Options:
*  ***-h, --help*** Show help message.
*  ***--start***  Load initial conditions starting with this dataset.
*  ***--end***    Last dataset of initial conditions to load.
*  ***--algo***   The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft
 
### gencon.py
Generate initial conditions.