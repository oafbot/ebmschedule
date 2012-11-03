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
config.batch = 1

for batch in range(0, config.batch):
    print "\nWriting initial conditions dataset No.", batch
    if(config.bigdata): 
        from inputs.BigModel import BigModel   
        model = BigModel(0, metrics, config, batch)
    else:
        from inputs.Model import Model  
        model = Model(0, metrics, config, batch)