class User:
    def __init__(self, dbu=None, username="", uid=0):
        if dbu is None:
            self.username = username
            self.uid = uid
        else:
            self.username = dbu.username
            self.uid = dbu.id

    def to_base_info_dict(self):
        return {"username": self.username,
                "id": self.uid if self.uid > 0 else "Not stated?"}
