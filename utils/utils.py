from typing import List, Set, Any, Tuple
import random

import datetime
from datetime import datetime as DatetimeT
import uuid
import traceback
import sys

from config import Config


def full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]  # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stack_str = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
        stack_str += '  ' + traceback.format_exc().lstrip(trc)
    return stack_str


def gen_token() -> Tuple[str, DatetimeT]:
    return uuid.uuid4().hex, datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.TOKEN_LIFETIME_SEC)


def shuffle_and_split_near_equal_parts(items: List[Any], amount: int) -> List[List[Any]]:
    if amount > len(items):
        raise Exception("Not possible to split list to more parts, than the length of the list")
    items_shuffled = list(items)
    random.shuffle(items_shuffled)
    result = [[] for _ in range(amount)]
    for i in range(len(items_shuffled)):  # TODO: Probably, not the best solution
        result[i % amount].append(items_shuffled[i])
    return result


def gen_rand_key() -> int:
    return random.randint(-Config.RANDOM_BORDER, Config.RANDOM_BORDER)


def str_list(items: List[Any], prefix: str = "", separator: str = "\n", suffix: str = "") -> str:
    return prefix + separator.join([str(item) for item in items]) + suffix


def take_n_random_from_set(values: Set[Any], k: int) -> List[Any]:
    assert len(values) >= k
    return random.choices(list(values), k=k)
