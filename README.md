EBM Scheduler
=============
### Algorithms
#### PushToRight:
If there are conflicts on the scheduled day, try to schedule by pushing one day forward.
#### PushToRightRelaxLeft:
If there are conflicts on the scheduled day, push one day back as long as a conflict exists until predetermined floor is reached. If task was not scheduled try pushing forward until ceiling is reached.

### Tools
#### crunch.py
Run main.py n number of times.
#### gencon.py
Generate initial conditions.
