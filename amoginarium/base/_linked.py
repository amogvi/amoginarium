"""
_linked.py
20. March 2024

globals

Author:
Nilusink
"""
from icecream import ic
import typing as tp


class BoundFunction(tp.TypedDict):
    func: tp.Callable
    args: tuple
    kwargs: dict


in_next_loop: list[BoundFunction] = []
_in_loop: dict[int, BoundFunction] = {}


def set_in_loop[**A, R](
    func: tp.Callable[A, R],
    *args: A.args,
    **kwargs: A.kwargs
) -> int:
    if len(_in_loop) > 0:
        new_key = max(_in_loop.keys()) + 1

    else:
        new_key = 0

    _in_loop[new_key] = {
        "func": func,
        "args": args,
        "kwargs": kwargs
    }

    return new_key


def reset_in_loop(key: int) -> None:
    _in_loop.pop(key)


def get_in_loop() -> list[BoundFunction]:
    return list(_in_loop.values())
