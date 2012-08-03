EBM Scheduler
=============
### Algorithm
#### PushToRight:
If there are conflicts on the scheduled day, try to schedule by pushing one day forward.
#### PushToRightRelaxLeft:
If there are conflicts on the scheduled day, push one day back as long as a conflict exists until predetermined floor is reached. If task was not scheduled try pushing forward until ceiling is reached.