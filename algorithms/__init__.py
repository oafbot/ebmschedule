class Algos:
    def __init__(self, model):
        import main
        from PushToRight import PushToRight
        from PushRightRelaxLeft import PushRightRelaxLeft
    
        for input in model:
            if(input.conf.algo == 0):
                self.algorithm = PushToRight(input)
            elif(input.conf.algo == 1):
                self.algorithm = PushRightRelaxLeft(input)
            else:
                pass