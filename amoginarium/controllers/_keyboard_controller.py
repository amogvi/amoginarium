"""
_keyboard_controller.py
25. January 2024

uses the keyboard as a controller

Author:
Nilusink
"""
from dataclasses import dataclass
import typing as tp
import keyboard

from ._base_controller import Controller


@dataclass(frozen=True)
class KeyboardControlls:
    up: str = "w"
    down: str = "s"
    left: str = "a"
    right: str = "d"
    press: str = "space"


class KeyboardController(Controller):
    def __init__(self) -> None:
        super().__init__()

        self._controlls = KeyboardControlls()

    def update(self):
        # read controlls
        self._keys.up = keyboard.is_pressed(self._controlls.up)
        self._keys.down = keyboard.is_pressed(self._controlls.down)
        self._keys.left = keyboard.is_pressed(self._controlls.left)
        self._keys.right = keyboard.is_pressed(self._controlls.right)
        self._keys.joy_btn = keyboard.is_pressed(self._controlls.press)
