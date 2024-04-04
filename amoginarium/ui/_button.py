"""
_button.py
26. March 2024

a button, what did you expect?

Author:
Nilusink
"""
import typing as tp
import pygame as pg

from ..logic import coord_t, convert_coord, Color, Vec2
from ..render_bindings import renderer, tColor


class Button:
    def __init__(
            self,
            position: coord_t,
            size: coord_t,
            text: str,
            color: tColor | Color,
            command: tp.Callable[[], None] = ...,
            radius: float = ...,
    ) -> None:
        self._position = convert_coord(position, Vec2)
        self._size = convert_coord(size, Vec2)
        self._radius = radius
        self._color = Color.from_255(70, 70, 70)
        self._hover_color = Color.from_255(90, 90, 90)
        self._border_color = Color.from_255(40, 40, 40)
        self._border_width = 5
        self._fg_color = Color.from_255(255, 255, 255)
        self._command = command
        self._text = text
        self._last_hover = False
        self._last_mouse = False

    def gl_draw(self) -> None:
        mouse_pos = pg.mouse.get_pos()
        hover = all([
            self._position.x <= mouse_pos[0] <= self._position.x + self._size.x,
            self._position.y <= mouse_pos[1] <= self._position.y + self._size.y
        ])

        # base box
        if self._radius is not ...:
            if self._border_width > 0:
                renderer.draw_rounded_rect(
                    self._position,
                    self._size,
                    self._border_color,
                    self._radius
                )

            renderer.draw_rounded_rect(
                self._position + self._border_width,
                self._size - 2 * self._border_width,
                self._hover_color if hover else self._color,
                self._radius
            )

        else:
            if self._border_width > 0:
                renderer.draw_rect(
                    self._position,
                    self._size,
                    self._border_color,
                )

            renderer.draw_rect(
                self._position + self._border_width,
                self._size - 2 * self._border_width,
                self._color,
            )

        # text
        renderer.draw_text(
            self._position + self._size / 2,
            # (
            #     self._position.x + self._size.x / 2,
            #     self._position.y + self._size.y * 1.5
            # ),
            self._text,
            self._fg_color,
            self._hover_color if hover else self._color,
            centered=True
        )

        # check if mouse down
        mouse_left, *_ = pg.mouse.get_pressed()
        if hover and not self._last_mouse and mouse_left:
            self._command()

        self._last_hover = hover
        self._last_mouse = mouse_left
