#!/usr/bin/python
import inputs, algorithms, outputs, metrics
import sys
from tests.Tests import Tests

if __name__ == "__main__":
    """Handle command line args."""
    algo    = sys.argv[1] if len(sys.argv)>1 else -1
    counter = sys.argv[2] if len(sys.argv)>2 else  0
    weight  = sys.argv[3] if len(sys.argv)>3 else  5
    relax   = sys.argv[4] if len(sys.argv)>4 else  3

    """"Initialize metrics."""
    metrics = metrics.Metrics()

    """Construct the model."""
    model = inputs.Inputs(counter, metrics, algo).model
    
    """Feed the model to the algorithm."""    
    algorithm = algorithms.Algos(model, weight, relax).algorithm
    
    """Run metrics."""
    metrics.run(algorithm)
    
    """Test Scheduling Output."""
    if algorithm.results.conf.testing:
        test = Tests(algorithm)
        
