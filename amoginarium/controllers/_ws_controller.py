"""
_ws_controller.py
01. February 2024

interfaces with a ws controller client

Author:
Nilusink
"""
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
            trigger_btn: bool = ...,
            joy_btn: bool = ...,
            joy_x: float = ...,
            joy_y: float = ...
    ) -> None:
        """
        controlls updates provided by the server
        """
        # apply a curve to the controller values
        self._keys.joy_x = self.joy_curve(
            (joy_x - 5e3) / 5e3,
            self.x_dead_zone
        )
        self._keys.joy_y = self.joy_curve(
            (joy_y - 5e3) / 5e3,
            self.y_dead_zone
        )

        # write button
        self._keys.shoot = trigger_btn
        self._keys.reload = joy_btn  # map joy click to reload
