"""
_utility_classes.py
25. January 2024

defines a few useful classes

Author:
Nilusink
"""
import typing as tp


class BetterDict:
    """
    each element is also accessible with instance.element
    """
    def __init__(self, **initial) -> None:
        for key, value in initial.items():
            setattr(self, key, value)

    def __setitem__(self, key: str, value: tp.Any) -> None:
        setattr(self, key, value)

    def __getitem__(self, item: str) -> tp.Any:
        return self.__dict__[item]

    def __delitem__(self, key) -> None:
        delattr(self, key)
