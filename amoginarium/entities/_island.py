"""
_island.py
26. January 2024

an island in the sky

Author:
Nilusink
"""
import typing as tp
import random

from ..render_bindings import draw_rect
from ..entities import VisibleEntity
from ..base import Walls
from ..logic import Vec2


class Island(VisibleEntity):
    def __init__(
            self,
            start: Vec2,
            size: Vec2,
            texture: str = ...
    ) -> None:
        self._size = size.copy()
        self._texture = texture

        super().__init__(
            size=size,
            initial_position=start
        )

        self.add(Walls)

    @classmethod
    def random_between(
        cls,
        x_start: int,
        x_end: int,
        y_start: int,
        y_end: int,
        x_size_start: int,
        x_size_end: int,
        y_size_start: int,
        y_size_end: int
    ) -> tp.Self:
        x = random.randint(x_start, x_end)
        y = random.randint(y_start, y_end)

        x_size = random.randint(x_size_start, x_size_end)
        y_size = random.randint(y_size_start, y_size_end)

        start = Vec2.from_cartesian(x, y)
        size = Vec2.from_cartesian(x_size, y_size)

        return cls(start, size)

    def gl_draw(self) -> None:
        draw_rect(
            self.world_position - self.size / 2,
            self.size,
            (.6, .4, .2)
        )
