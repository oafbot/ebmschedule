import main
from PushToRight import PushToRight
from PushRightRelaxLeft import PushRightRelaxLeft

for input in main.inputs.inputs:
    if(input.conf.algo == 0):
        PushToRight(input)
    elif(input.conf.algo == 1):
        PushRightRelaxLeft(input)
    else:
        pass