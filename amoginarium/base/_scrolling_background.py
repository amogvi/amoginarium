"""
_scrolling_background.py
27. January 2024

A parralax-scrolling background

Author:
Nilusink
"""
# from OpenGL
from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D, glEnable
from OpenGL.GL import glMatrixMode, glLoadIdentity, glTranslate, glDisable
from OpenGL.GL import glVertex, glBegin, glTexCoord2f, glEnd, glGenTextures
from OpenGL.GL import glFlush
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT
from OpenGL.GL import GL_TEXTURE_WRAP_T, GL_TEXTURE_MIN_FILTER
from OpenGL.GL import GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGBA
from OpenGL.GL import GL_UNSIGNED_BYTE, GL_MODELVIEW, GL_QUADS
from PIL import Image

from icecream import ic

import pygame as pg
import os


def load_texture(filename: str) -> tuple[int, tuple[int]]:
    """
    load an image texture

    :returns: texture_id, (width, height)
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"failed to load texture \"{filename}\"")

    im = Image.open(filename)

    # Flip the image vertically (since OpenGL's origin is at bottom-left)
    im = im.transpose(Image.FLIP_TOP_BOTTOM)

    width, height = im.size[0], im.size[1]
    img_data = im.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)

    return texture_id, (width, height)


def draw_textured_quad(
    texture_id: int,
    x, y,
    width, height
) -> None:
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslate(x, y, 0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)

    glVertex(0, 0, 0)
    glTexCoord2f(0, 0)
    glVertex(width, 0, 0)
    glTexCoord2f(0, 1)
    glVertex(width, height, 0)
    glTexCoord2f(1, 1)
    glVertex(0, height, 0)
    glTexCoord2f(1, 0)

    glEnd()
    glDisable(GL_TEXTURE_2D)
    glFlush()


class ScrollingBackground:
    def __init__(
        self,
        background_file: str,
        scrolling_part_file: str,
        screen_width: int,
        screen_height: int,
    ) -> None:
        self._texture_id, self._texture_size = load_texture(background_file)
        ic(self._texture_id)
        # self._bg_image = pg.image.load(background_file).convert()
        # self._scroll_image = pg.image.load(scrolling_part_file).convert_alpha()
        # self._image_size = self._scroll_image.get_size()
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
        draw_textured_quad(self._texture_id, 0, 0, *self._texture_size)
        # surface.blit(self._bg_image, (0, 0))

        # for i in range(self._screen_width // self._image_size[0] + 1):
        #     surface.blit(
        #         self._scroll_image,
        #         (self._position + self._image_size[0] * i, 0)
        #     )


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

        # self._images.append(pg.image.load(
        #     self._directory + sorted(os.listdir(self._directory))[1]
        # ).convert_alpha())
        for file in sorted(os.listdir(self._directory)):
            tid, size = load_texture(self._directory + file)
            self._textures.append(tid)
            self._sizes.append(size)

    def scroll(self, value: float) -> None:
        """
        scroll by `value` pixels (first layer)
        """
        self._position -= value

    def draw(self, surface: pg.surface.Surface) -> None:
        """
        draw background to surface
        """
        n_layers = len(self._textures)-1
        for layer in range(n_layers, -1, -1):
            image_pos = self._position % self._screen_width
            image_pos *= self._multiplier**(n_layers-layer)
            image_pos = int(image_pos % self._screen_width)
            image_pos -= self._screen_width

            draw_textured_quad(
                self._textures[layer],
                image_pos, 0,
                *self._sizes[layer]
            )
            draw_textured_quad(
                self._textures[layer],
                image_pos + self._screen_width, 0,
                *self._sizes[layer]
            )

            # surface.blit(
            #     self._images[layer],
            #     (image_pos, 0),
            # )
            # surface.blit(
            #     self._images[layer],
            #     (image_pos + self._screen_width, 0),
            # )
