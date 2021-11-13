from typing import List, Set, Any
import random


def split_into_near_equal_parts(items: List[Any], size: int) -> List[List[Any]]:
    random.shuffle(items)

    amount = (len(items) + size - 1) // size

    parts = []
    for i in range(amount):
        parts.append(items[i * size: min(len(items), (i + 1) * size)])

    return parts


def str_list(items: List[Any], prefix: str = "", separator: str = "\n", suffix: str = "") -> str:
    return prefix + separator.join([str(item) for item in items]) + suffix


def take_n_random_from_set(values: Set[Any], k: int) -> List[Any]:
    assert len(values) >= k
    return random.choices(list(values), k=k)
