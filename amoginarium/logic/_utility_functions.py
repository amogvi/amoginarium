"""
_utility_functions.py
19. March 2024

a few useful functions

Author:
Nilusink
"""
from ._vectors import Vec2


type coord_t = tuple[int, int] | tuple[float, float] | Vec2


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


def is_related(a: object, b: object, depth: int = 2) -> bool:
    """
    check if either is parent or child or self

    depths:
    1: true if a == b
    2: true if a == b or parent
    3: true if all of the above or siblings
    4: coalition
    """
    is_same = a == b
    if depth == 1:
        return is_same

    is_parented = False

    try:
        is_parented = is_parented or a.parent == b
    except AttributeError:
        pass

    try:
        is_parented = is_parented or b.parent == a
    except AttributeError:
        pass

    if depth == 2:
        return is_same or is_parented

    try:
        is_sibling = a.parent == b.parent
        if depth == 3:
            return is_same or is_parented or is_sibling

    except AttributeError:
        return is_same or is_parented

    try:
        is_coalition = a.root == b.root

        if depth == 4:
            return is_same or is_parented or is_sibling or is_coalition

    except AttributeError:
        return is_same or is_parented or is_sibling


def convert_coord[A](
        coord: coord_t,
        convert_to: type[A] = tuple
) -> A:
    """
    accepts both tuple and Vec2
    """
    if convert_to is Vec2:
        if isinstance(coord, Vec2):
            return coord

        return Vec2.from_cartesian(*coord)

    if convert_to is tuple:
        if isinstance(coord, tuple):
            return coord

        return coord.xy
