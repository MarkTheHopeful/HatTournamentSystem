from typing import List
from typing import Counter as CounterT
import enum
from collections import Counter


class GameStatus(enum.Enum):
    not_started = 0  # No results available
    completed = 1  # Results are ready


class Game:
    def __init__(self, participants_uid: List[int], words: List[str]):
        self.participants_uid: List[int] = participants_uid
        self.words: List[str] = words
        self.state: GameStatus = GameStatus.not_started
        self.result: CounterT[int, int] = Counter(participants_uid)

    def conclude_result(
        self, results: CounterT[int]
    ) -> bool:  # TODO: replace with an exception
        if self.state == GameStatus.completed:
            return False
        if set(self.participants_uid) != set(
            results.keys()
        ):  # FIXME: bad way to do this
            return False
        self.result = results
        self.state = GameStatus.completed
        return True
