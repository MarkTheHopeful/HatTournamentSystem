from typing import List, Set, Any
import random


def split_into_near_equal_parts(items: List[Any], amount: int) -> List[List[Any]]:
    if amount > len(items):
        raise Exception("Not possible to split list to more parts, than the length of the list")
    result = [[] for _ in range(amount)]
    for i in range(len(items)):  # TODO: Probably, not the best solution
        result[i % amount].append(items[i])
    return result


def str_list(items: List[Any], prefix: str = "", separator: str = "\n", suffix: str = "") -> str:
    return prefix + separator.join([str(item) for item in items]) + suffix


def take_n_random_from_set(values: Set[Any], k: int) -> List[Any]:
    assert len(values) >= k
    return random.choices(list(values), k=k)
