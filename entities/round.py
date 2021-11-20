class Round:
    def __init__(self, dbu=None, name="", difficulty=0):
        if dbu is None:
            self.name = name
            self.difficulty = difficulty
        else:
            self.name = dbu.name
            self.difficulty = dbu.difficulty
