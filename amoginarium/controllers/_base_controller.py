"""
_base_controller.py
25. January 2024

all controller types should inherit from this

Author:
Nilusink
"""
from dataclasses import dataclass
import typing as tp


from ..logic import Vec2


@dataclass
class Controlls():
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    joy_btn: bool = False
    joy_x: float = .5
    joy_y: float = .5


class _Controllers:
    """
    a collection of all controllers
    """
    _controllers: list["Controller"]
    _callbacks: dict[int, tp.Callable]

    def __init__(self) -> None:
        self._controllers = []
        self._callbacks = {}

    @property
    def controllers(self) -> list["Controller"]:
        return self._controllers.copy()
    
    def append(self, controller: "Controller") -> None:
        """
        add a new controller to the group
        """
        self._controllers.append(controller)
        self._on_new_controller(controller)

    def _on_new_controller(self, controller: "Controller") -> None:
        """
        actual callback method
        """
        for callback in self._callbacks.values():
            callback(controller)

    def on_new_controller(
        self,
        callback: tp.Callable[["Controller"], tp.Any]
    ) -> int:
        """
        add a callback for adding new controllers
        """
        if len(self._callbacks) == 0:
            new_id = 0

        else:
            new_id = max(list(self._callbacks.keys())) + 1
    
        self._callbacks[new_id] = callback

        return new_id
    
    def remove_callback(self, cid: int) -> None:
        """
        remove a callback with it's callback-id
        """
        if cid in self._callbacks:
            self._callbacks.pop(cid)
            return
        
        raise ValueError(f"Invalid cid: {cid}")


Controllers = _Controllers()


class Controller:
    _keys: Controlls

    def __new__(cls) -> tp.Self:
        new_instance = super(Controller, cls).__new__(cls)

        # append every new instance to controllers
        Controllers.append(new_instance)

        return new_instance


    def __init__(self) -> None:
        self._keys = Controlls()

    def update(self, delta: float) -> None:
        """
        update the control inputs
        """

    @property
    def up(self) -> bool:
        return self._keys.up
    
    @property
    def down(self) -> bool:
        return self._keys.down

    @property
    def left(self) -> bool:
        return self._keys.left

    @property
    def right(self) -> bool:
        return self._keys.right

    @property
    def joy_btn(self) -> bool:
        return self._keys.joy_btn

    @property
    def joy_x(self) -> bool:
        return self._keys.joy_x

    @property
    def joy_y(self) -> bool:
        return self._keys.joy_y

    @property
    def joy_polar(self) -> Vec2:
        return Vec2.from_cartesian(self.joy_x, self.joy_y)

    @property
    def controlls(self) -> Controlls:
        return self._keys.copy()
