#!/usr/bin/python
import inputs, algorithms, outputs
import sys
from tests.Tests import Tests

if __name__ == "__main__":
    """Handle command line args."""
    counter = sys.argv[1] if len(sys.argv)>1 else 0  
    weight  = sys.argv[2] if len(sys.argv)>2 else 1
    
    
    """Construct the model."""
    model = inputs.Inputs(counter).model
    
    """Feed the model to the algorithm."""    
    algorithm = algorithms.Algos(model, weight).algorithm
    
    """Configure outputs."""
    # output = outputs.Outputs(model).output
    
    """Test Scheduling Output."""
    if(algorithm.results.conf.testing):
        test = Tests(algorithm)

    # Display Metrics
    # metrics

