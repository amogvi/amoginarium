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


from ._console_colors import CC, get_fg_color


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

            prefix = ic.prefix()
            prefix_time = prefix[:-3]
            prefix_arrow = prefix[-3:]

            print(
                f"{get_fg_color(36)}{prefix_time}"
                f"{get_fg_color(247)}{prefix_arrow}{CC.fg.GREEN}"
                f"running {CC.fg.MAGENTA}{func.__name__}{get_fg_color(36)}, "
                f"called by {CC.fg.MAGENTA}{calframe[1][3]}{get_fg_color(36)}" +
                (f"with {args, kwargs}" if show_args else "") +
                f"{CC.ctrl.ENDC}"
            )
    
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                print(
                    f"{CC.fg.CYAN}{ic.prefix()}{CC.fg.RED}"
                    f"{'':#>5} exception in {CC.fg.ORANGE}\"{func.__name__}\""
                    f"{CC.fg.RED} {'':#<5}\n{format_exc()}"
                    f"{CC.ctrl.ENDC}"
                )

                if on_fail is not ...:
                    on_fail(e)

        return wrapper
    return decorator
