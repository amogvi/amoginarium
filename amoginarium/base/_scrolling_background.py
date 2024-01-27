"""
_scrolling_background.py
27. January 2024

A parralax-scrolling background

Author:
Nilusink
"""
import pygame as pg
import os


class ScrollingBackground:
    def __init__(
        self,
        background_file: str,
        scrolling_part_file: str,
        screen_width: int,
        screen_height: int,
    ) -> None:
        self._bg_image = pg.image.load(background_file).convert()
        self._scroll_image = pg.image.load(scrolling_part_file).convert_alpha()
        self._image_size = self._scroll_image.get_size()
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
        surface.blit(self._bg_image, (0, 0))

        for i in range(self._screen_width // self._image_size[0] + 1):
            surface.blit(
                self._scroll_image,
                (self._position + self._image_size[0] * i, 0)
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

        self._images = []

        # self._images.append(pg.image.load(
        #     self._directory + sorted(os.listdir(self._directory))[1]
        # ).convert_alpha())
        for file in sorted(os.listdir(self._directory)):
            self._images.append(pg.image.load(
                self._directory + file
            ).convert_alpha())

    def scroll(self, value: float) -> None:
        """
        scroll by `value` pixels (first layer)
        """
        self._position -= value

    def draw(self, surface: pg.surface.Surface) -> None:
        """
        draw background to surface
        """
        n_layers = len(self._images)-1
        for layer in range(n_layers, -1, -1):
            image_pos = self._position % self._screen_width
            image_pos *= self._multiplier**(n_layers-layer)
            image_pos = int(image_pos % self._screen_width)
            image_pos -= self._screen_width

            surface.blit(
                self._images[layer],
                (image_pos, 0),
            )
            surface.blit(
                self._images[layer],
                (image_pos + self._screen_width, 0),
            )
