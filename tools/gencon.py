# ============================================
# = Script to generate initial conditions    =
# ============================================

import sys
sys.path.append( '../' )

from inputs.Config import Config 
config = Config()
config.reset = True
config.fixed = True

import metrics
metrics = metrics.Metrics()

# ===========================================
# = ALL YOUR CONFIGURATIONS ARE BELOW TO US =
# ===========================================
config.bigdata = True
config.cap = 10


if(config.bigdata): 
    from inputs.BigModel import BigModel   
    model = BigModel(0, metrics, config)
else:
    from inputs.Model import Model  
    model = Model(0, metrics, config)