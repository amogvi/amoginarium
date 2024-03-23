"""
_keyboard_controller.py
25. January 2024

uses the keyboard as a controller

Author:
Nilusink
"""
from dataclasses import dataclass
import pygame as pg

from ._base_controller import Controller


@dataclass(frozen=True)
class Keyboardcontrols:
    up: str = pg.K_w
    down: str = pg.K_s
    left: str = pg.K_a
    right: str = pg.K_d
    press: str = pg.K_SPACE


class KeyboardController(Controller):
    def __init__(self) -> None:
        super().__init__("0")

        self._controls = Keyboardcontrols()

    def update(self, delta):
        pressed_keys = pg.key.get_pressed()

        # read controls
        up = pressed_keys[self._controls.up]
        down = pressed_keys[self._controls.down]
        left = pressed_keys[self._controls.left]
        right = pressed_keys[self._controls.right]
        self._keys.jump = pressed_keys[self._controls.press]

        self._keys.shoot = pressed_keys[pg.K_e]
        self._keys.reload = pressed_keys[pg.K_r]

        # set joystick position (using wasd keys)
        self._keys.joy_x = -left + right
        self._keys.joy_y = -down + up
