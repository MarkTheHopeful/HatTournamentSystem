class User:
    def __init__(self, dbu=None, username=""):
        if dbu is None:
            self.username = username
        else:
            self.username = dbu.username

    def to_base_info_dict(self):
        return {"username": self.username}
