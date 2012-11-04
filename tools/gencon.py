#!/usr/local/bin/python
import sys
import argparse

sys.path.append( '../' )
from inputs.Config import Config

config = Config()
config.reset = True
config.fixed = True

import metrics
metrics = metrics.Metrics()


# ============================================
# = Script to generate initial conditions    =
# ============================================

if __name__ == "__main__":
    """Handle command line args."""
    parser = argparse.ArgumentParser(prog='gencon')
    parser.add_argument('--plat',  type=int,  help='The Platform ID to generate conditions for.')
    parser.add_argument('--batch', type=int,  help='How many files to create.')
    parser.add_argument('--cap',   type=int,  help='How many datasets to write in the xml.')
    parser.add_argument('--simp',  action="store_false", default=True, 
                                   help='Switch between big data and the a simple model.')
    args = vars(parser.parse_args())
    
    config.bigdata  = args['simp' ] if args['simp' ] is not None else True 
    config.cap      = args['cap'  ] if args['cap'  ] is not None else 10
    config.batch    = args['batch'] if args['batch'] is not None else 1
    config.platform = args['plat' ] if args['plat' ] is not None else 1
    
    if not config.bigdata: config.platform = 0

    for batch in range(0, config.batch):
        print "\nWriting initial conditions dataset No.", batch, "for platform", config.platform
        if(config.bigdata): 
            from inputs.BigModel import BigModel   
            model = BigModel(0, metrics, config, batch)
        else:
            from inputs.Model import Model  
            model = Model(0, metrics, config, batch)