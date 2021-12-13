class Subround:
    def __init__(self, dbu=None, name="", uid=0):
        if dbu is None:
            self.name = name
            self.uid = uid
        else:
            self.name = dbu.name
            self.uid = dbu.id

    def to_base_info_dict(self):
        return {"name": self.name, "id": self.uid}
