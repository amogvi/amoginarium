"""
_base_renderer.py
21. March 2024

prototype renderer

Author:
Nilusink
"""
import typing as tp

from ..logic import Color, coord_t


type Color3 = tuple[float, float, float]
type Color4 = tuple[float, float, float, float]
type tColor = Color3 | Color4


class BaseRenderer:
    @staticmethod
    def set_color(color: Color | tColor) -> None:
        """
        set gColor
        """
        raise NotImplementedError

    @staticmethod
    def load_texture(
            filename: str,
            size: coord_t | None = None,
            mirror: tp.Literal["x", "y", "xy"] = "",
    ) -> tuple[int, tuple[int]]:
        """
        load an image texture

        :returns: texture_id, (width, height)
        """
        raise NotImplementedError

    @staticmethod
    def draw_textured_quad(
            texture_id: int,
            pos: coord_t,
            size: coord_t,
            convert_global: bool = True
    ) -> None:
        """
        draw a rectangle with a texture
        """
        raise NotImplementedError

    def draw_circle(
            self,
            center: coord_t,
            radius: float,
            num_segments: int,
            color: Color | tColor,
            convert_global: bool = True
    ) -> None:
        """
        draw a circle
        """
        raise NotImplementedError

    def draw_rect(
            self,
            start: coord_t,
            size: coord_t,
            color: Color | tColor,
            convert_global: bool = True
    ) -> None:
        """
        draw a rectangle
        """
        raise NotImplementedError

    def draw_dashed_circle(
            self,
            center: coord_t,
            radius: float,
            num_segments: int,
            color: Color | tColor,
            thickness: int = 1,
            convert_global: bool = True
    ) -> None:
        """
        draw a dashed circle with num_segments segments
        """
        raise NotImplementedError

    def draw_line(
            self,
            start: coord_t,
            end: coord_t,
            color: Color | tColor,
            global_position: bool = True,
            convert_global: bool = True
    ) -> None:
        """
        draw a simple line
        """
        raise NotImplementedError
