from typing import List
from typing import Counter as CounterT
import enum
from play_pair import PlayPair
from collections import Counter


class GameStatus(enum.Enum):
    not_started = 0  # No results available
    completed = 1  # Results are ready


class Game:
    def __init__(self, participants: List[PlayPair], words: List[str]):
        self.participants: List[PlayPair] = participants
        self.words: List[str] = words
        self.state: GameStatus = GameStatus.not_started
        self.result: CounterT[PlayPair, int] = Counter(participants)

    def conclude_result(self, results: Counter[PlayPair, int]) -> bool:  # TODO: replace with an exception
        if self.state == GameStatus.completed:
            return False
        if set(self.participants) != set(results.keys()):  # FIXME: bad way to do this
            return False
        self.result = results
        return True
