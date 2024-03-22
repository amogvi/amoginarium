"""
_scrolling_background.py
27. January 2024

A parralax-scrolling background

Author:
Nilusink
"""
# from OpenGL
from icecream import ic

import pygame as pg
import os

from ..render_bindings import renderer


class ScrollingBackground:
    def __init__(
        self,
        background_file: str,
        scrolling_part_file: str,
        screen_width: int,
        screen_height: int,
    ) -> None:
        self._texture_id, self._texture_size = renderer.load_texture(
            background_file
        )
        ic(self._texture_id)
        self._position = 0

        self._screen_width = screen_width
        self._screen_height = screen_height

    def scroll(self, value: float) -> None:
        """
        scroll by `value` pixels (first layer)
        """
        self._position -= value

    def draw(self, surface: pg.surface.Surface) -> None:
        """
        draw background to surface
        """
        renderer.draw_textured_quad(
            self._texture_id,
            (0, 0),
            self._texture_size
        )


class ParalaxBackground:
    def __init__(
        self,
        directory: str,
        screen_width: int,
        screen_height: int,
        parallax_multiplier: float = 1.2
    ) -> None:
        self._directory = directory + "/layers/"
        self._multiplier = parallax_multiplier
        self._position = 0

        self._screen_width = screen_width
        self._screen_height = screen_height

        self._textures = []
        self._sizes = []

        for file in sorted(os.listdir(self._directory)):
            # self._images.append(pg.image.load(
            #     self._directory + file
            # ).convert_alpha())

            tid, _ = renderer.load_texture(
                self._directory + file,
                (screen_width, screen_height)
            )
            self._textures.append(tid)
            self._sizes.append((screen_width, screen_height))

    @property
    def position(self) -> float:
        """
        get the position of the top layer
        """
        return -self._position * self._multiplier**len(self._textures)

    def scroll(self, value: float) -> None:
        """
        scroll by `value` pixels (first layer)
        """
        if self._position-value <= 0:
            self._position -= value

    def draw(self) -> None:
        """
        draw background to surface
        """
        n_layers = len(self._textures)-1
        for layer in range(n_layers, -1, -1):
            image_pos = self._position + 10 % self._screen_width
            image_pos *= self._multiplier**(n_layers-layer)
            image_pos = int(image_pos % self._screen_width)
            image_pos -= self._screen_width

            renderer.draw_textured_quad(
                self._textures[layer],
                (image_pos, 0),
                self._sizes[layer]
            )
            renderer.draw_textured_quad(
                self._textures[layer],
                (image_pos + self._screen_width, 0),
                self._sizes[layer]
            )
