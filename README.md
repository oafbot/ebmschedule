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
	$ ./main.py [algorithm] [data] [weight] [relax] [sort]
	
#### Example:
	$ ./main.py 1 0 5 3 +
	
* ***Algorithm*** is the algorithm to use. 0 is PushRight, 1 is PushRight-RelaxLeft.
* ***Data*** is the initial conditions to load. Ranges from 0 to as many datasets as was generated.
* ***Weight*** is the weight applied to sorting algorithm. Ranges from 0 to 10 (represents 0.0 to 1.0)
* ***Relax*** is the percentage of interval to relax left. Ranges from 1 to 3 (represents 25% to 75%)
* ***Sort*** is the sorting to be used by the Algorithm. Options: + for on , - for off, and ~ for reverse.

## Tools
### crunch.py
Run main.py N number of times with varying weights and relaxing (if relax left algorithm).

#### Usage: 
	$ ./crunch.py [-h] [--start START] [--end END] [--algo ALGO] [--sort SORT]
#### Example:
	$ ./crunch.py --algo 1 --start 0 --end 0 

#### Options:
*  ***-h, --help*** Show help message.
*  ***--start***  Load initial conditions starting with this dataset.
*  ***--end***    Last dataset of initial conditions to load.
*  ***--algo***   The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft
*  ***--sort***   Sorting to be used by the ALgorithm. Options: on, off, reverse

### gencon.py
Generate initial conditions.