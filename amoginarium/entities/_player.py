"""
_player.py
26. January 2024

defines a player

Author:
Nilusink
"""
import pygame as pg

from ..base import GravityAffected, FrictionXAffected
from ._base_entity import LRImageEntity
from ..controllers import Controller
from ..logic import Vec2


class Player(LRImageEntity):
    _image_right_path: str = "assets/images/amogus64right.png"
    _image_left_path: str = "assets/images/amogus64left.png"
    _movement_acceleration: float = 700
    _max_movement_speed: float = 70

    def __init__(
        self,
        controller: Controller,
        facing: Vec2 = ...,
        initial_position: Vec2 = ...,
        initial_velocity: Vec2 = ...,
        size: int = 64

    ) -> None:
        self._controller = controller

        # load image
        self._image_right = pg.transform.scale(
            pg.image.load(self._image_right_path),
            (size, size)
        )
        self._image_left = pg.transform.scale(
            pg.image.load(self._image_left_path),
            (size, size)
        )
        self._image_size = size

        super().__init__(
            facing,
            initial_position,
            initial_velocity,
        )

        self.add(GravityAffected, FrictionXAffected)

    def update(self, delta):
        self._controller.update(delta)

        # update controls
        if self._controller.joy_x > .5:
            self.acceleration.x += self._movement_acceleration

        elif self._controller.joy_x < .5:
            self.acceleration.x -= self._movement_acceleration

        if self._controller.down and self.on_ground:
            self.velocity.y = -400

        super().update(delta)

    @property
    def on_ground(self) -> bool:
        out = self.position.y + self.size > 900
        return out
