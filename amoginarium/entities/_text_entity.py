"""
_text_entity.py
06. June 2024

an entity displaying text

Author:
Nilusink
"""
# from icecream import ic
import typing as tp
import pygame as pg

from ..logic import coord_t, Color, Vec2, convert_coord
from ..render_bindings import renderer, tColor
from ..base import Drawn, Updated


class TextEntity(pg.sprite.Sprite):
    def __init__(
            self,
            _coalition,
            position: coord_t,
            text: str,
            color: Color | tColor = ...,
            bg_color: Color | tColor = ...
    ) -> None:
        if color is ...:
            color = Color.white(255)

        elif issubclass(type(color), tp.Iterable):
            color = Color.from_255(*color)

        if bg_color is ...:
            bg_color = Color.from_255(0, 0, 0, 0)

        elif issubclass(type(color), tp.Iterable):
            bg_color = Color.from_255(*bg_color)

        self._pos = convert_coord(position, Vec2)
        self._text = text
        self._color = color
        self._bg_color = bg_color

        super().__init__()
        self.add(Drawn)

    def gl_draw(self):
        now = self._pos - Updated.world_position
        renderer.draw_text(
            now,
            self._text,
            self._color,
            self._bg_color
        )
