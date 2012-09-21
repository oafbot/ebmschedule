#!/usr/bin/python
def main():
    import inputs, algorithms, outputs
    import sys
    
    if(len(sys.argv)>1):
        count = sys.argv[1]
    else:
        count = 0
    
    model = inputs.define(count)
    algorithms = algorithms.define(model)
    outputs = outputs.define(model)

    return [model, algorithms, outputs]
    
    # inputs.input(count)
    # algorithms.algorithm()
    # outputs.outputs()
    
    print count
    
if __name__ == "__main__":
    ret = main() 
    model = ret[0]
    algorithms = ret[1]
    outputs = ret[2] 

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
