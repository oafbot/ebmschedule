import sys
sys.path.append( '../' )
from inputs.Config import Config 
config = Config()
config.bigdata = 0
config.reset = True
config.fixed = True
config.cap = 1000

if(config.bigdata): 
    from inputs.BigModel import BigModel   
    model = BigModel(0, config)
else:
    from inputs.Model import Model  
    model = Model(0, config)