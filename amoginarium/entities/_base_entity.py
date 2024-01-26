"""
_base_entity.py
25. January 2024

defines the most basic form of an entity

Author:
Nilusink
"""
import pygame as pg
import math as m

from ..base import Updated, Drawn
from ..logic import Vec2


class Entity(pg.sprite.Sprite):
    facing: Vec2
    position: Vec2
    velocity: Vec2
    acceleration: Vec2

    def __init__(
        self,
        size: Vec2 = ...,
        facing: Vec2 = ...,
        initial_position: Vec2 = ...,
        initial_velocity: Vec2 = ...
    ) -> None:
        self.size = Vec2.from_cartesian(1, 1) if size is ... else size
        self.facing = Vec2.from_cartesian(1, 0) if facing is ... else facing
        self.position = Vec2() if initial_position is ... else initial_position
        self.velocity = Vec2() if initial_velocity is ... else initial_velocity
        self.acceleration = Vec2()

        super().__init__()

        self.update_rect()
        self.add(Updated)

    def on_ground(self) -> bool:
        return self.position.y + self.size.y > 1080

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )

    def update(self, delta: float) -> None:
        # update velocity and position
        self.velocity += self.acceleration * delta
        self.position += self.velocity * delta

        # re-calculate pygame stuff
        self.last_angle = self.velocity.angle

        self.update_rect()


class VisibleEntity(Entity):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add(Drawn)


class ImageEntity(VisibleEntity):
    image: pg.surface.Surface
    _original_image: pg.surface.Surface

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.image = pg.transform.rotate(
            self._original_image.copy(),
            -self.velocity.angle * (180 / m.pi)
        )

    def update(self, delta: float) -> None:
        orig_center = self.rect.center
        # try:
        self.image = pg.transform.rotate(
            self._original_image.copy(),
            -self.velocity.angle * (180 / m.pi)
)

        # except pg.error:
        #     self.image = self._original_image.copy()
        self.rect = self.image.get_rect(center=orig_center)
        self.last_angle = self.velocity.angle

        super().update(delta)


class LRImageEntity(VisibleEntity):
    _image_right: pg.surface.Surface
    _image_left: pg.surface.Surface

    def __init__(self, *args, **kwargs) -> None:
        self.image = self._image_right.copy()

        super().__init__(*args, **kwargs)

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )

    def update(self, delta: float) -> None:
        if self.facing.x > 0:
            self.image = self._image_right.copy()

        elif self.facing.x < 0:
            self.image = self._image_left.copy()

        super().update(delta)
