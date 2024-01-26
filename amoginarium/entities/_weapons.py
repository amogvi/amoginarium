"""
_weapons.py
26. January 2024

minigun go brrrrrt

Author:
Nilusink
"""
from time import perf_counter
import pygame as pg

from ._base_entity import VisibleEntity
from ..base import GravityAffected
from ..logic import Vec2


class Bullet(VisibleEntity):
    _image_path: str = "assets/images/bullet.png"

    def __init__(
        self,
        initial_position: Vec2,
        initial_velocity: Vec2,
        casing: bool = False
    ) -> None:
        size = Vec2.from_cartesian(10, 10)

        self.image = pg.transform.scale(
            pg.image.load(self._image_path),
            size.xy
        )

        self._start_time = perf_counter()

        super().__init__(
            size=size,
            initial_position=initial_position.copy(),
            initial_velocity=initial_velocity.copy()
        )

        self.add(GravityAffected)

        # if not casing:
        #     self.add(WallBouncer)

    @property
    def on_ground(self) -> bool:
        return self.position.y > 1000

    def update(self, delta):
        if any([
            self.position.y > 1000,
            self.position.x < 0,
            self.position.x > 2000,
            perf_counter() - self._start_time > 2,
            self.on_ground
        ]):
            self.kill()
            return

        # double gravity (because why not)
        self.acceleration.y *= 2

        super().update(delta)
