#!/usr/local/bin/python
import inputs, algorithms, metrics
import sys
from tests.Tests import Tests

if __name__ == "__main__":
    """Handle command line args."""
    algo    = sys.argv[1] if len(sys.argv)>1 else -1
    counter = sys.argv[2] if len(sys.argv)>2 else  0
    weight  = sys.argv[3] if len(sys.argv)>3 else  5
    relax   = sys.argv[4] if len(sys.argv)>4 else  3
    sort    = sys.argv[5] if len(sys.argv)>5 else '+'
    plat    = sys.argv[6] if len(sys.argv)>6 else  1
    trace   = sys.argv[7] if len(sys.argv)>7 else  1
    batch   = sys.argv[8] if len(sys.argv)>8 else  0    
    
    """"Initialize metrics."""
    metrics = metrics.Metrics()

    """Construct the model."""
    model = inputs.Inputs(counter, metrics, algo, plat, trace, batch).model

    """Feed the model to the algorithm."""
    algorithm = algorithms.Algos(model, weight, relax, sort).algorithm

    """Run metrics."""
    metrics.run(algorithm)

    """Test scheduling output."""
    if algorithm.results.conf.testing:
        test = Tests(algorithm)
