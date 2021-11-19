class Tournament:
    def __init__(self, dbu=None, name=""):
        if dbu is None:
            self.name = name
        else:
            self.name = dbu.name

    def to_base_info_dict(self):
        return {"name": self.name}
