import enum
from typing import List
from typing import Counter as CounterT
from collections import Counter
from game import Game, GameStatus
from utils import split_into_near_equal_parts
from word import WordBank


class RoundStatus(enum.Enum):
    not_started = 0
    completed = 1


class Round:
    def __init__(self, name: str, participants_uid: List[int], difficulty: int, word_bank: WordBank) -> None:
        self.name: str = name
        self.participants_uid: List[int] = participants_uid
        self.difficulty: int = difficulty
        self.word_bank = word_bank
        self.subrounds: List[Subround] = []
        self.results: CounterT[int, int] = Counter(participants_uid)
        self.state = RoundStatus.not_started

    def add_subround(self, participants: List[int], words_to_take: int) -> bool:
        if self.state == RoundStatus.completed:
            return False
        if len(participants) < 2:
            return False
        if not set(participants).issubset(self.participants_uid):
            return False
        new_subround: Subround = Subround(participants, [str(word) for word in
                                                         self.word_bank.extract_words_by_difficulty(self.difficulty,
                                                                                                    words_to_take)])
        self.subrounds.append(new_subround)
        return True

    def conclude_results(self) -> bool:
        if self.state == RoundStatus.completed:
            return False
        for subround in self.subrounds:
            if subround.state != SubroundStatus.completed:
                return False

        for subround in self.subrounds:
            self.results += subround.results

        self.state = RoundStatus.completed

    def get_top_n(self, n: int) -> List[int]:
        if n > len(self.participants_uid):
            return []  # FIXME: replace with exception
        if self.state != RoundStatus.completed:
            return []
        return [x[0] for x in self.results.most_common(n)]


class SubroundStatus(enum.Enum):
    not_split = 0
    split_not_played = 1
    completed = 2


class Subround:
    def __init__(self, participants: List[int], words: List[str]) -> None:
        self.state: SubroundStatus = SubroundStatus.not_split
        self.participants_uid: List[int] = participants
        self.words: List[str] = words
        self.results: CounterT[int, int] = Counter(participants)
        self.games: List[Game] = []

    def split_players_to_games(self, amount_of_games: int) -> bool:  # TODO: replace bool with exceptions
        if self.state != SubroundStatus.not_split:
            return False
        if amount_of_games * 2 > len(self.participants_uid):
            return False

        parts = split_into_near_equal_parts(self.participants_uid, amount_of_games)
        for part in parts:
            self.games.append(Game(part, self.words))

        self.state = SubroundStatus.split_not_played
        return True

    def conclude_results(self) -> bool:  # TODO: replace bool with exceptions
        if self.state == SubroundStatus.not_split or self.state == SubroundStatus.completed:
            return False
        for game in self.games:
            if game.state != GameStatus.completed:
                return False
        for game in self.games:
            self.results += game.result

        self.state = SubroundStatus.completed
        return True
