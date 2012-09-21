class Outputs:
    def __init__(self, model):
        from Output import Output

        for input in model:
            self.output = Output(input)

        # from Calendar import Calendar
        # Calendar = Calendar()