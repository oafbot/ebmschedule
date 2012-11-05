EBM Scheduler
=============
## Purpose
Optimization algorithms to solve the general problem of Optimal Maintenance Scheduling for 
Aircraft or other types of vehicles when there are limited resources available to deliver such 
maintenance to a fleet of aircraft or other kind of bundle of vehicles. 

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
* ***Data***      is the initial conditions to load. Ranges from 0 to as many datasets as was generated.
* ***Weight***    is the weight applied to sorting algorithm. Ranges from 0 to 10 (represents 0.0 to 1.0)
* ***Relax***     is the percentage of interval to relax left. Ranges from 1 to 3 (represents 25% to 75%)
* ***Sort***      is the sorting to be used by the Algorithm. Options: + for on , - for off, and ~ for reverse.
* ***Plat***      is the platform id of the equipment to run the scheduling scripts on.
* ***Trace***     is the flag to turn off console output. Default is on. Input 0 to turn off.
* ***Batch***	  corresponds to the initial conditions xml file to load.

## Tools
### crunch.py
Run main.py N number of times with varying weights and relaxing (if relax left algorithm).

#### Usage: 
	$ ./crunch.py [-h] [--start START] [--end END] [--algo ALGO] [--sort SORT] [--plat PLAT] [--batch BATCH] 
#### Example:
	$ ./crunch.py --algo 1 --start 0 --end 0 --plat 2

#### Options:
*  ***-h, --help*** Show help message.
*  ***--start***  Load initial conditions starting with this dataset.
*  ***--end***    Last dataset of initial conditions to load.
*  ***--algo***   The algorithm to use. 0 is PushRight, 1 is PushRightRelaxLeft
*  ***--sort***   Sorting to be used by the ALgorithm. Options: on, off, reverse
*  ***--plat***   The platform to run the algorithm on.
*  ***--batch***  Batch process X number of initial conditions.

### autocrunch.py
Run crunch with all permutations on variables: algorithms, weights, relax factors, sorting rules.

#### Usage:
	$ ./autocrunch.py [platform] [batch]
	
#### Example:
	$ ./autocrunch.py 2 0
	
* ***Platform*** Run scripts on this platform id.
* ***Batch***    How many dataset xml files to load for the batch operation.   

### gencon.py
Generate initial conditions.

#### Usage:
	$ ./gencon [-h] [--plat PLAT] [--batch BATCH] [--cap CAP] [--simp]
	
#### Example:
	$ ./gencon --plat 2 --cap 10 --batch 10

#### Options:	
*  ***-h, --help*** Show this help message and exit
*  ***--plat***		The Platform ID to generate conditions for.
*  ***--batch***	How many files to create.
*  ***--cap***		How many datasets to write in the xml.
*  ***--simp***		Switch between big data and the a simple model.
