"""
_ws_controller.py
01. February 2024

interfaces with a ws controller client

Author:
Nilusink
"""
from typing import overload
from icecream import ic

from ._base_controller import Controller


class WsController(Controller):
    x_dead_zone: float = .1
    y_dead_zone: float = .1

    def __init__(self, controller_id: str) -> None:
        super().__init__(controller_id)

    def update(self, delta):
        """
        updates are provided by the communications thread,
        so the default update funcion is ignored
        """
        pass

    def update_controlls(
        self,
        **controls
    ) -> None:
        """
        controlls updates provided by the server
        """
        joy_updated = False
        for control, value in controls:
            if value is ...:
                continue

            match value:
                # add curve to joystick axis
                case "joy_x":
                    self._keys.joy_x = self.joy_curve(
                        value,
                        self.x_dead_zone
                    )
                    joy_updated = True

                case "joy_y":
                    self._keys.joy_y = self.joy_curve(
                        value,
                        self.y_dead_zone
                    )
                    joy_updated = True

                # directly translate all other values
                case _:
                    if hasattr(self._keys, control):
                        setattr(
                            self._keys,
                            control,
                            value
                        )
                        continue

                    ic(f"tried setting {control} to {value}")

        # for this controller, "up" on the joystick also means jump
        if joy_updated:
            self._keys.jump = self._keys.joy_y > 0

    @overload
    def update_controlls(
        self,
        jump: bool = ...,
        reload: bool = ...,
        shoot: bool = ...,
        idk: bool = ...,
        joy_btn: bool = ...,
        joy_x: float = ...,
        joy_y: float = ...
    ) -> None:
        ...
