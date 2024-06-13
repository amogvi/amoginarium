"""
_utils.py
22. March 2024

generally useful functions

Author:
Nilusink
"""
from icecream import ic
import inspect

from ._console_colors import get_fg_color, CC


def get_caller_name() -> str:
    """
    get the name of the function that called this context
    """
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)

    return calframe[1][3]


def print_ic_style(value: str) -> str:
    prefix = ic.prefix
    if not isinstance(prefix, str):
        prefix = prefix()

    prefix_time = prefix[:-3]
    prefix_arrow = prefix[-3:]

    print(
        f"{get_fg_color(36)}{prefix_time}"
        f"{get_fg_color(247)}{prefix_arrow}{get_fg_color(36)}" +
        value +
        f"{CC.ctrl.ENDC}"
    )
