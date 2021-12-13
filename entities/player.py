class Player:
    def __init__(self, dbu=None, name_first="", name_second="", uid=0):
        if dbu is None:
            self.name_first = name_first
            self.name_second = name_second
            self.uid = uid
        else:
            self.name_first = dbu.name_first
            self.name_second = dbu.name_second
            self.uid = dbu.id

    def to_base_info_dict(self):
        return {
            "name_first": self.name_first,
            "name_second": self.name_second,
            "id": self.uid if self.uid != 0 else "Not stated?",
        }
