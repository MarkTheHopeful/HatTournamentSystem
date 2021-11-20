class Word:
    def __init__(self, dbu=None, text="", difficulty=0):
        if dbu is None:
            self.text = text
            self.difficulty = difficulty
        else:
            self.text = dbu.text
            self.difficulty = dbu.difficulty

    def to_base_info_dict(self):
        return {"text": self.text,
                "difficulty": self.difficulty}
