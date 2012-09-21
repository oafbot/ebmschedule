#!/usr/bin/python
class Main:
    def __init__(self):
        import inputs, algorithms, outputs
        import sys

        if(len(sys.argv)>1):
            self.counter = sys.argv[1]
        else:
            self.counter = 0
        
        self.Model = inputs.Inputs(self.counter).model
        self.Outputs = outputs.Outputs(self.Model).output
        self.Algorithm = algorithms.Algorithms(self.Model).algorithm
    
# if __name__ == "__main__":
Main()


# inputs
# # inputs = Inputs()
# 
# # Run Scheduling Algorithms
# algorithms
# 
# # Output
# outputs
# 
# # Test Scheduling Output
# # tests
# 
# # Display Metrics
# # metrics
