#!/usr/bin/python
import inputs, algorithms, outputs
import sys
from tests.Tests import Tests

if __name__ == "__main__":
    """Handle command line args."""
    if(len(sys.argv)>1):
        counter = sys.argv[1]
    else:
        counter = 7
    
    """Construct the model."""
    model = inputs.Inputs(counter).model
    
    """Feed the model to the algorithm."""    
    algorithm = algorithms.Algos(model).algorithm
    
    """Configure outputs."""
    # output = outputs.Outputs(model).output
    
    """Test Scheduling Output."""
    if(algorithm.results.conf.testing):
        test = Tests(algorithm)

    # Display Metrics
    # metrics

