"""
_utility_functions.py
19. March 2024

a few useful functions

Author:
Nilusink
"""


def classname(c: object) -> str:
    """
    get the name of an obect class
    """
    return c.__class__.__name__


def is_parent(parent: object, child: object) -> bool:
    """
    check parent is the parent of child
    """
    if not hasattr(child, "parent"):
        return False

    return parent == child.parent


def is_related(a: object, b: object) -> bool:
    """
    check if either is parent or child
    """
    return is_parent(a, b) or is_parent(b, a)
