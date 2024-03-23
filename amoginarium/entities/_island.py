"""
_island.py
26. January 2024

an island in the sky

Author:
Nilusink
"""
import typing as tp
import math as m
import random

from ..render_bindings import renderer
from ..entities import VisibleEntity
from ..base import Walls
from ..logic import Vec2


class Island(VisibleEntity):
    _island_single_texture: int = ...

    _island_single_right_texture: int = ...
    _island_single_left_texture: int = ...
    _island_single_top_texture: int = ...
    _island_single_bottom_texture: int = ...

    _island_left_texture: int = ...
    _island_left_inv_texture: int = ...

    _island_middle_texture: int = ...
    _island_middle_inv_texture: int = ...

    _island_right_texture: int = ...
    _island_right_inv_texture: int = ...

    _island_wall_right_texture: int = ...
    _island_wall_left_texture: int = ...

    _dirt_hole_texture: int = ...
    _dirt_texture: int = ...

    _image_size: tuple[int, int] = (64, 64)

    def __new__(cls, *args, **kwargs):
        # only load texture once
        if cls._island_single_texture is ...:
            cls.load_textures()

        return super(Island, cls).__new__(cls)

    @classmethod
    def load_textures(cls) -> None:
        if cls._island_single_texture is not ...:
            return

        cls._island_single_texture, _ = renderer.load_texture(
            "assets/images/grass_single.png",
            cls._image_size
        )

        cls._island_single_right_texture, _ = renderer.load_texture(
            "assets/images/grass_single_right.png",
            cls._image_size
        )
        cls._island_single_left_texture, _ = renderer.load_texture(
            "assets/images/grass_single_left.png",
            cls._image_size
        )
        cls._island_single_top_texture, _ = renderer.load_texture(
            "assets/images/grass_single_top.png",
            cls._image_size
        )
        cls._island_single_bottom_texture, _ = renderer.load_texture(
            "assets/images/grass_single_bottom.png",
            cls._image_size
        )

        cls._island_left_texture, _ = renderer.load_texture(
            "assets/images/grass_left.png",
            cls._image_size,
            mirror="x"
        )
        cls._island_left_inv_texture, _ = renderer.load_texture(
            "assets/images/grass_left_bottom.png",
            cls._image_size,
            mirror="x"
        )

        cls._island_middle_texture, _ = renderer.load_texture(
            "assets/images/grass_middle.png",
            cls._image_size,
            mirror="x"
        )
        cls._island_middle_inv_texture, _ = renderer.load_texture(
            "assets/images/grass_middle_bottom.png",
            cls._image_size,
            mirror="x"
        )

        cls._island_right_texture, _ = renderer.load_texture(
            "assets/images/grass_right.png",
            cls._image_size,
            mirror="x"
        )
        cls._island_right_inv_texture, _ = renderer.load_texture(
            "assets/images/grass_right_bottom.png",
            cls._image_size,
            mirror="x"
        )

        cls._island_wall_right_texture, _ = renderer.load_texture(
            "assets/images/grass_wall_right.png",
            cls._image_size,
            mirror=""
        )
        cls._island_wall_left_texture, _ = renderer.load_texture(
            "assets/images/grass_wall_right.png",
            cls._image_size,
            mirror="x"
        )

        cls._dirt_texture, _ = renderer.load_texture(
            "assets/images/dirt.png",
            cls._image_size,
            mirror="x"
        )
        cls._dirt_hole_texture, _ = renderer.load_texture(
            "assets/images/dirt_hole.png",
            cls._image_size,
            mirror="x"
        )

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
        start_pos = self.world_position - self.size / 2

        # fill island with dirt
        n_rows = m.ceil(self.size.y / self._image_size[1])
        n_columns = m.ceil(self.size.x / self._image_size[0])
        for row in range(n_rows):
            row_offset = self._image_size[1] * row

            for column in range(n_columns):
                texture = self._dirt_texture

                # corners
                if n_rows == n_columns == 1:
                    texture = self._island_single_texture

                elif column == 0:
                    if n_rows == 1:
                        texture = self._island_single_right_texture

                    elif row == 0:
                        texture = self._island_left_texture

                        if n_columns == 1:
                            texture = self._island_single_top_texture

                    elif row == n_rows - 1:
                        texture = self._island_left_inv_texture

                        if n_columns == 1:
                            texture = self._island_single_bottom_texture

                    else:
                        texture = self._island_wall_right_texture

                elif column == n_columns - 1:
                    if n_rows == 1:
                        texture = self._island_single_left_texture

                    elif row == 0:
                        texture = self._island_right_texture

                    elif row == n_rows - 1:
                        texture = self._island_right_inv_texture

                    else:
                        texture = self._island_wall_left_texture

                # center pieces
                elif row == 0:
                    texture = self._island_middle_texture

                elif row == n_rows - 1:
                    texture = self._island_middle_inv_texture

                # else:
                #     # random holes
                #     if random.randint(0, 20) == 13:
                #         texture = self._dirt_hole_texture

                column_offset = self._image_size[0] * column
                pos = start_pos + Vec2.from_cartesian(
                    column_offset,
                    row_offset
                )
                size = self._image_size
                renderer.draw_textured_quad(
                    texture,
                    pos,
                    size
                )
