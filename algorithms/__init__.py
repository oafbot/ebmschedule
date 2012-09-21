def define(model):
    import main
    from PushToRight import PushToRight
    from PushRightRelaxLeft import PushRightRelaxLeft
    
    for input in model:
        if(input.conf.algo == 0):
            return PushToRight(input)
        elif(input.conf.algo == 1):
            return PushRightRelaxLeft(input)
        else:
            pass

# if __name__ == "__main__":
#     # algorithm()
#     pass