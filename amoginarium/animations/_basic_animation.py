"""
_basic_animation.py
19. March 2024

An animation made from multiple images

Author:
Nilusink
"""
from threading import Thread
import typing as tp
import time
import os

from ..render_bindings import draw_textured_quad, load_texture
from ..base._linked import set_in_loop, reset_in_loop
from ..logic import Vec2


def play_animation(
    position: Vec2,
    sizes: tp.Iterable[Vec2],
    textures: tp.Iterable[int],
    delay=.2
) -> None:

    # position.x -= size.x / 2
    # position.y -= size.y / 2

    def inner():
        for size, texture in zip(sizes, textures):
            key = set_in_loop(
                draw_textured_quad,
                texture,
                *position.xy,
                *size.xy
            )
            # img = pg.image.load(directory+"/"+image)
            # img = pg.transform.scale(img, (size.x, size.y))
            # x = Game.blit(surface, img, position)
            time.sleep(delay)
            reset_in_loop(key)

    Thread(target=inner).start()


class ImageAnimation:
    """
    play an animation from a directory
    """
    _textures: list[int] = ...
    _sizes: list[int] = ...

    def __init__(
        self,
        directory: tp.LiteralString,
    ) -> None:
        self._directory = directory

    def load_textures(self, filetype: str = ".png", size: Vec2 = None) -> None:
        """
        load all textures required for the animation
        """
        images = [self._directory + "/" + file for file in os.listdir(
            self._directory
        ) if file.endswith(".png")]

        self._textures = []
        self._sizes = []
        for image in images:
            texture, size = load_texture(
                image,
                size
            )
            self._textures.append(texture)
            self._sizes.append(Vec2.from_cartesian(*size))

    def draw(
        self,
        position: Vec2,
        delay=.2,
        size: Vec2 = ...
    ) -> None:
        """
        play the recently loaded animation
        """
        if self._textures is ...:
            self.load_textures()

        play_animation(
            position - self._sizes[0] / 2,
            self._sizes if size is ... else len(self._sizes) * [size],
            self._textures,
            delay
        )


# constant animations
explosion = ImageAnimation("./assets/images/animations/explosion/")
