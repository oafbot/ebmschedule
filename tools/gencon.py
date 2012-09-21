import sys
sys.path.append( '../' )
from inputs.Config import Config 
config = Config()

if(config.bigdata): 
    from inputs.BigModel import BigModel   
    model = BigModel()
else:
    from inputs.Model import Model   
    model = Model()