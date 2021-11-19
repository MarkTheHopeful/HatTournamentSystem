class PlayPair:
    def __init__(self, name_first: str, name_second: str, uid: int) -> None:
        self.name_first: str = name_first
        self.name_second: str = name_second
        self.uid: int = uid

    def __str__(self) -> str:
        return f"Pair: {self.name_first}, {self.name_second}"

    def get_partner(self, name: str) -> str:
        if self.name_first == name:
            return self.name_second
        return self.name_first
