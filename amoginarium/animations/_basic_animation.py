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

from ..render_bindings import draw_textured_quad
from ..base import BaseGame
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
        # images = [file for file in os.listdir(directory) if file.endswith(".png")]
        # images.sort()

        for size, texture in zip(sizes, textures):
            BaseGame().run_in_loop(
                draw_textured_quad,
                texture,
                *position.xy,
                *size.xy
            )
            # img = pg.image.load(directory+"/"+image)
            # img = pg.transform.scale(img, (size.x, size.y))
            # x = Game.blit(surface, img, position)
            time.sleep(delay)

    Thread(target=inner).start()


class ImageAnimation:
    """
    play an animation from a directory
    """

    def __init__(self, directory, ):
        ...


