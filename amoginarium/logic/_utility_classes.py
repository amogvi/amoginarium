"""
_utility_classes.py
25. January 2024

defines a few useful classes

Author:
Nilusink, melektron
"""
from time import perf_counter
import typing as tp
import asyncio
import inspect


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


class SimpleLock:
    def __init__(self) -> None:
        self.__locked_by: str = ...

    def aquire(
        self,
        timeout: float = 0
    ) -> bool:
        """
        :param timeout: timeout in seconds
        """
        start = perf_counter()

        curframe = inspect.currentframe()
        called_by = inspect.getouterframes(curframe, 2)[1][3]

        while perf_counter() - start > timeout or timeout == 0:
            if self.__locked_by is ...:
                self.__locked_by = called_by
                return True

        return False

    def release(self) -> None:
        """
        release a lock (only works from same function)
        """
        curframe = inspect.currentframe()
        called_by = inspect.getouterframes(curframe, 2)[1][3]

        if called_by != self.__locked_by:
            raise NameError("Lock can't be released from different function!")

        self.__locked_by = ...


class _BaseTimer:
    def _run_callback(self, cb: tp.Callable | None):
        if cb is not None:
            asyncio.create_task(cb())


class WDTimer(_BaseTimer):
    def __init__(self, timeout: float) -> None:
        """
        Watchdog timer that continuously down from the time
        specified in timeout and but can be reset to the start at any time
        using the refresh() method.
        If the timer reaches zero (timeout) it fires a callback.
        When the timer is restarted the first time after reaching zero using
        refresh() (or the first time it this method is called) a restart
        callback fires.)

        timeout: time to count down for in seconds
        """
        self._timeout: float = timeout
        self._timer_task: asyncio.Task = None
        self._on_timeout_cb: tp.Callable = None
        self._on_restart_cb: tp.Callable = None

    def on_timeout(self, cb: tp.Callable):
        """
        Registers a callback handler (must be async) for the timeout event
        (aka. when the timer isn't refreshed before the timeout time.)

        Note: There can only be one callback, registering a second one
        overwrites the first one.
        """
        self._on_timeout_cb = cb

        return self

    def on_restart(self, cb: tp.Callable):
        """
        Registers a callback handler (must be async) for the restart event
        (aka. when the timer restarts counting after a timeout or
        on initial start)

        Note: There can only be one callback, registering a second one
        overwrites the first one.
        """
        self._on_restart_cb = cb

        return self

    def refresh(self):
        """
        Resets the timer so it starts counting all over again if it is already
        counting and starts it if it has finished counting down or is started
        the first time.
        This causes restart callback to run if the timer isn't running
        at the time of calling.
        """

        # first start
        if self._timer_task is None:
            self._run_callback(self._on_restart_cb)
            self._timer_task = asyncio.create_task(self._timer_fn())

        # after timeout
        elif self._timer_task.done():
            self._run_callback(self._on_restart_cb)
            self._timer_task = asyncio.create_task(self._timer_fn())

        # while it is still running
        else:
            self._timer_task.cancel()
            self._timer_task = asyncio.create_task(self._timer_fn())

        return self

    def cancel(self) -> None:
        """
        cancel the timer
        """
        if self._timer_task is not None:
            self._timer_task.cancel()

    async def _timer_fn(self):
        await asyncio.sleep(self._timeout)
        self._run_callback(self._on_timeout_cb)

    def __del__(self):
        if self._timer_task is None:
            return self
        self._timer_task.cancel()
        self._timer_task = None
