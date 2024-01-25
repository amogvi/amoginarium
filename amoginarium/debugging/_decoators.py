"""
_basegame.py
25. January 2024

Defines the core game

Author:
Nilusink
"""
from traceback import format_exc
from icecream import ic
import typing as tp
import inspect


from ._console_colors import *


def run_with_debug(
            show_args: bool = False,
            on_fail: tp.Callable[[Exception], tp.Any] = ...
        ):
    """
    run a function with debugging and exception printing
    """
    def decorator[**A, R](func: tp.Callable[A, R]):
        def wrapper(*args: A.args, **kwargs: A.kwargs) -> R:
            # get caller name
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)

            print(
                f"{CYAN}{ic.prefix()}{BLUE}"
                f"running {MAGENTA}\"{func.__name__}\"{BLUE}, "
                f"called by {MAGENTA}\"{calframe[1][3]}\"{BLUE}"+
                (f"with {args, kwargs}" if show_args else "")+
                f"{ENDC}"
            )
    
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                print(
                    f"{CYAN}{ic.prefix()}{RED}"
                    f"{'':#>5} exception in {ORANGE}\"{func.__name__}\"{RED} "
                    f"{'':#<5}\n{format_exc()}"+
                    ENDC
                )

                if on_fail is not ...:
                    on_fail(e)

        return wrapper
    return decorator
