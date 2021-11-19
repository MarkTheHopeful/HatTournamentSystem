class Player:
    def __init__(self, dbu=None, name_first="", name_second=""):
        if dbu is None:
            self.name_first = name_first
            self.name_second = name_second
        else:
            self.name_first = dbu.name_first
            self.name_second = dbu.name_second

    def to_base_info_dict(self):
        return {"name_first": self.name_first,
                "name_second": self.name_second}
