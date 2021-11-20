class IdPair:
    def __init__(self, dbu=None, id_1=0, id_2=0):
        if dbu is None:
            self.id_1 = id_1
            self.id_2 = id_2
        else:
            self.id_1 = dbu.id_1
            self.id_2 = dbu.id_2
