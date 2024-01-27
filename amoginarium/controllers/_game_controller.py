"""
_game_controller.py
26. January 2024

uses the keyboard as a controller

Author:
Nilusink
"""
from dataclasses import dataclass
import pygame as pg

from ._base_controller import Controller


@dataclass(frozen=True)
class ControllerKeybmap:
    y: int = 0
    b: int = 1
    a: int = 2
    x: int = 3
    l1: int = 4
    r1: int = 5
    l2: int = 6
    r2: int = 7
    lopt: int = 8
    ropt: int = 9
    ljoy: int = 10
    rjoy: int = 11
    menu: int = 12


class GameController(Controller):
    x_dead_zone: float = .1
    y_dead_zone: float = .1

    def __init__(self, pygame_joystick: pg.joystick.JoystickType) -> None:
        if not pygame_joystick.get_init():
            pygame_joystick.init()

        self._joystick = pygame_joystick

        super().__init__()

    def btn(self, n_button: int) -> bool:
        """
        get a joystick button
        """
        return self._joystick.get_button(n_button)

    def joy_curve(
        self,
        value: float,
        deadzone: float = 0
    ) -> float:
        """
        apply a specific curve for joystick values
        """
        value = (value / abs(value)) * max(0, abs(value) - deadzone)

        return value * (1 / (1 - deadzone))

    def update(self, delta):
        # read controlls
        self._keys.shoot = self.btn(ControllerKeybmap.r2)
        self._keys.reload = self.btn(ControllerKeybmap.b)
        self._keys.jump = self.btn(ControllerKeybmap.a)
        self._keys.idk = self.btn(ControllerKeybmap.x)

        # set joystick position
        self._keys.joy_x = self.joy_curve(
            self._joystick.get_axis(0),
            self.x_dead_zone
        )
        self._keys.joy_y = self.joy_curve(
            self._joystick.get_axis(1),
            self.y_dead_zone
        )

        self._keys.joy_btn = self.btn(ControllerKeybmap.ljoy)

    def rumble(
        self,
        low_frequency,
        high_frequency,
        duration
    ) -> None:
        self._joystick.rumble(low_frequency, high_frequency, duration)

    def stop_rumble(self) -> None:
        self._joystick.stop_rumble()

    def __str__(self) -> None:
        return f"<{self.__class__.__name__}, name={self._joystick.get_name()}>"
