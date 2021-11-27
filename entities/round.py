class Round:
    def __init__(self, dbu=None, name="", difficulty=0, uid=0):
        if dbu is None:
            self.name = name
            self.difficulty = difficulty
            self.uid = uid
        else:
            self.name = dbu.name
            self.difficulty = dbu.difficulty
            self.uid = dbu.id

    def to_base_info_dict(self):
        return {"name": self.name,
                "difficulty": self.difficulty,
                "id": self.uid if self.uid != 0 else "Not stated?"}
