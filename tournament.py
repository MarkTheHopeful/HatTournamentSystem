from typing import List, Tuple, Dict
from round import Round
from play_pair import PlayPair
from word import WordBank


class Tournament:
    VERSION: str = "0.0.2"

    def __init__(self, uid: int) -> None:
        self.uid = uid

        self.uid_to_play_pair: Dict[int, PlayPair] = dict()
        self.player_name_to_pair_uid: Dict[str, int] = dict()
        self.pairs_added: int = 0

        self.words: WordBank = WordBank()

        self.rounds: List[Round] = list()

    def add_word(self, word_text: str, difficulty: int) -> Tuple[bool, int]:
        return self.words.add_word(word_text, difficulty)

    def delete_word(self, word_text: str) -> bool:
        return self.words.delete_word(word_text)

    def add_play_pair(self, first_player: str, second_player: str) -> bool:
        if first_player in self.player_name_to_pair_uid.keys() or second_player in self.player_name_to_pair_uid.keys():
            return False

        pair_uid: int = self.pairs_added
        pair: PlayPair = PlayPair(first_player, second_player, pair_uid)
        self.pairs_added += 1

        self.uid_to_play_pair[pair_uid] = pair
        self.player_name_to_pair_uid[first_player] = pair_uid
        self.player_name_to_pair_uid[second_player] = pair_uid
        return True

    def delete_play_pair(self, first_player: str, second_player: str) -> bool:
        if first_player not in self.player_name_to_pair_uid.keys() \
                or second_player not in self.player_name_to_pair_uid.keys():
            return False

        if self.player_name_to_pair_uid[first_player] != self.player_name_to_pair_uid[second_player]:
            return False

        pair_uid: int = self.player_name_to_pair_uid[first_player]
        del self.uid_to_play_pair[pair_uid]
        del self.player_name_to_pair_uid[first_player]
        del self.player_name_to_pair_uid[second_player]

        return True

    def create_round(self, participants_uid: List[int], difficulty: int, name: str) -> None:
        new_round: Round = Round(name, participants_uid, difficulty, self.words)
        self.rounds.append(new_round)
