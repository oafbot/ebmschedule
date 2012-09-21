#!/usr/bin/python
import inputs, algorithms, outputs
import sys

if __name__ == "__main__":
    if(len(sys.argv)>1):
        counter = sys.argv[1]
    else:
        counter = 0

    model = inputs.Inputs(counter).model    
    algorithm = algorithms.Algorithms(model).algorithm
    # output = outputs.Outputs(model).output

    # Test Scheduling Output
    # tests

    # Display Metrics
    # metrics

