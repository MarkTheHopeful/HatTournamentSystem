from collections import defaultdict
from utils.utils import take_n_random_from_set
from typing import List, DefaultDict, Set, Dict, Tuple


class Word:
    def __init__(self, text: str, difficulty: int, uid: int) -> None:
        self.text: str = text
        self.difficulty: int = difficulty
        self.uid: int = uid

    def __str__(self) -> str:
        return self.text


class WordBank:
    def __init__(self) -> None:
        self.uid_to_words: Dict[int, Word] = dict()
        self.word_text_to_uid: Dict[str, int] = dict()
        self.difficulty_to_words: DefaultDict[int, Set[int]] = defaultdict(set)
        self.words_added: int = 0

    def add_word(self, text: str, difficulty: int) -> Tuple[bool, int]:
        if text in self.word_text_to_uid.keys():
            return False, -1

        word_uid = self.words_added
        self.words_added += 1

        self.uid_to_words[word_uid] = Word(text, difficulty, word_uid)
        self.word_text_to_uid[text] = word_uid
        self.difficulty_to_words[difficulty].add(word_uid)
        return True, word_uid

    def delete_word(self, word_text: str) -> bool:
        if word_text not in self.word_text_to_uid.keys():
            return False

        word_uid = self.word_text_to_uid[word_text]
        self.difficulty_to_words[self.uid_to_words[word_uid].difficulty].remove(
            word_uid
        )
        del self.word_text_to_uid[word_text]
        del self.uid_to_words[word_uid]
        return True

    def extract_words_by_difficulty(self, difficulty: int, amount: int) -> List[Word]:
        result = take_n_random_from_set(self.difficulty_to_words[difficulty], amount)
        for word in result:
            self.delete_word(word)
        return result
