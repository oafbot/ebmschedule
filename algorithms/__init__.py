class Algos:
    """Routing and instatiation for algorithms."""    
    def __init__(self, model, weight, relax, sort):
        import main
        from PushToRight import PushToRight
        from PushRightRelaxLeft import PushRightRelaxLeft
        from RelaxLeftOnUsage import RelaxLeftOnUsage
        # from PushToLeft import PushToLeft

        for input in model:
            if(input.conf.algo == 0):
                self.algorithm = PushToRight(input, float(weight), sort)
            elif(input.conf.algo == 1):
                self.algorithm = PushRightRelaxLeft(input, float(weight), float(relax), sort)
            elif(input.conf.algo == 2):
                self.algorithm = RelaxLeftOnUsage(input, float(weight), float(relax), sort)
                #self.algorithm = PushToLeft(input, float(weight))