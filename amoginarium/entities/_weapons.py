"""
_weapons.py
26. January 2024

minigun go brrrrrt

Author:
Nilusink
"""
from time import perf_counter
from random import randint
import pygame as pg

from ..base import GravityAffected, CollisionDestroyed, Bullets, Updated, Drawn
from ._base_entity import VisibleEntity, Entity
from ..logic import Vec2


class Bullet(VisibleEntity):
    _image_path: str = "assets/images/bullet.png"
    _damage: float = 1

    def __init__(
        self,
        parent: Entity,
        initial_position: Vec2,
        initial_velocity: Vec2,
        casing: bool = False
    ) -> None:
        size = Vec2.from_cartesian(10, 10)
        self._casing = casing
        self._parent = parent

        if casing:
            self.image = pg.transform.scale(
                pg.image.load(self._image_path).convert_alpha(),
                size.xy
            )

        else:
            self.image = pg.surface.Surface(
                size.xy,
                pg.SRCALPHA,
                32
            )
            pg.draw.circle(
                self.image,
                (163, 157, 116),
                (size / 2).xy,
                size.length / 4
            )

        self._start_time = perf_counter()

        super().__init__(
            size=size,
            initial_position=initial_position.copy(),
            initial_velocity=initial_velocity.copy()
        )

        self.add(GravityAffected)

        if not casing:
            self.add(Bullets, CollisionDestroyed)

    @property
    def on_ground(self) -> bool:
        return self.position.y > 1000

    @property
    def damage(self) -> float:
        return self._damage if not self._casing else 0

    @property
    def parent(self) -> Entity:
        return self._parent

    def hit(self, _damage: float) -> None:
        self.kill()

    def hit_someone(self, target_hp: float) -> None:
        self.kill()

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

    def kill(self) -> None:
        if all([
            self._casing,
            0 <= self.position.x <= 1920
        ]):
            self.remove(
                Updated,
                CollisionDestroyed,
                GravityAffected
            )
            return

        self.remove(Drawn)

        super().kill()
