class Word:
    def __init__(self, dbu=None, text="", difficulty=0, uid=0):
        if dbu is None:
            self.text = text
            self.difficulty = difficulty
            self.uid = uid
        else:
            self.text = dbu.text
            self.difficulty = dbu.difficulty
            self.uid = dbu.id

    def to_base_info_dict(self):
        return {
            "text": self.text,
            "difficulty": self.difficulty,
            "id": self.uid if self.uid > 0 else "Not stated?",
        }
