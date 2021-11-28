from typing import List, Set, Any
import random

import datetime
import uuid
import traceback
import sys

from config import Config

SEPARATOR = '\t'


def convert_array_to_string(array, sep=SEPARATOR, auto_type_caster=str):
    return sep.join(map(auto_type_caster, array))


def convert_string_to_array(string, sep=SEPARATOR, auto_type_caster=str):
    return list(map(auto_type_caster, string.split(sep)))


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


def gen_token():
    return uuid.uuid4().hex, datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.TOKEN_LIFETIME_SEC)


def split_into_near_equal_parts(items: List[Any], amount: int) -> List[List[Any]]:
    if amount > len(items):
        raise Exception("Not possible to split list to more parts, than the length of the list")
    result = [[] for _ in range(amount)]
    for i in range(len(items)):  # TODO: Probably, not the best solution
        result[i % amount].append(items[i])
    return result


def gen_rand_key():
    return random.randint(-Config.RANDOM_BORDER, Config.RANDOM_BORDER)


def str_list(items: List[Any], prefix: str = "", separator: str = "\n", suffix: str = "") -> str:
    return prefix + separator.join([str(item) for item in items]) + suffix


def take_n_random_from_set(values: Set[Any], k: int) -> List[Any]:
    assert len(values) >= k
    return random.choices(list(values), k=k)
