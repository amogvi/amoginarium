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
class KeyboardControlls:
    up: str = pg.K_w
    down: str = pg.K_s
    left: str = pg.K_a
    right: str = pg.K_d
    press: str = pg.K_SPACE


class KeyboardController(Controller):
    def __init__(self) -> None:
        super().__init__()

        self._controlls = KeyboardControlls()

    def update(self, delta):
        pressed_keys = pg.key.get_pressed()

        # read controlls
        up = pressed_keys[self._controlls.up]
        down = pressed_keys[self._controlls.down]
        left = pressed_keys[self._controlls.left]
        right = pressed_keys[self._controlls.right]
        self._keys.jump = pressed_keys[self._controlls.press]

        self._keys.shoot = pressed_keys[pg.K_e]
        self._keys.reload = pressed_keys[pg.K_r]

        # set joystick position (using wasd keys)
        self._keys.joy_x = -left + right
        self._keys.joy_y = -down + up
