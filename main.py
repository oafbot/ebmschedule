#!/usr/bin/python
import inputs, algorithms, outputs
import sys
from tests.Tests import Tests

if __name__ == "__main__":

    if(len(sys.argv)>1):
        counter = sys.argv[1]
    else:
        counter = 0

    model = inputs.Inputs(counter).model    
    algorithm = algorithms.Algorithms(model).algorithm
    # output = outputs.Outputs(model).output

    # Test Scheduling Output
    if(algorithm.results.conf.testing):
        test = Tests(algorithm.results)

    # Display Metrics
    # metrics

