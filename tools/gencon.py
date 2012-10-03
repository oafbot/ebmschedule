import sys
sys.path.append( '../' )
from inputs.Config import Config 
config = Config()
config.reset = True
config.fixed = True
# ===========================================
# = ALL YOUR CONFIGURATIONS ARE BELOW TO US =
# ===========================================
config.bigdata = True
config.cap = 1


if(config.bigdata): 
    from inputs.BigModel import BigModel   
    model = BigModel(0, config)
else:
    from inputs.Model import Model  
    model = Model(0, config)