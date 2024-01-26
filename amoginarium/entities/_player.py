"""
_player.py
26. January 2024

defines a player

Author:
Nilusink
"""
import pygame as pg

from ..base import GravityAffected, FrictionXAffected, HasBars
from ._base_entity import LRImageEntity
from ..controllers import Controller
from ._weapons import Bullet
from ..logic import Vec2


class Player(LRImageEntity):
    _image_right_path: str = "assets/images/amogus64right.png"
    _image_left_path: str = "assets/images/amogus64left.png"
    _gun_path: str = "assets/images/minigun.png"
    _movement_acceleration: float = 700
    _max_hp: int = 20
    _hp: int = 0

    def __init__(
        self,
        controller: Controller,
        facing: Vec2 = ...,
        initial_position: Vec2 = ...,
        initial_velocity: Vec2 = ...,
        size: int = 64

    ) -> None:
        self._hp = self._max_hp

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
        self._gun_image_right = pg.transform.rotate(
            pg.transform.scale(
                pg.image.load(self._gun_path),
                (size * .8, size * .8)
            ),
            20
        )
        self._gun_image_left = pg.transform.flip(
            self._gun_image_right,
            1,
            0
        )
        self._image_size = size

        super().__init__(
            size=Vec2.from_cartesian(size, size),
            facing=facing,
            initial_position=initial_position,
            initial_velocity=initial_velocity,
        )

        self.add(GravityAffected, FrictionXAffected, HasBars)

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def hp(self) -> int:
        return self._hp

    def update(self, delta):
        self._controller.update(delta)

        # update controls
        if self._controller.joy_x > 0:
            self.acceleration.x += self._movement_acceleration
            self.facing.x = 1

        elif self._controller.joy_x < 0:
            self.acceleration.x -= self._movement_acceleration
            self.facing.x = -1

        if self._controller.down and self.on_ground:
            self._controller.rumble(300, 2000, 500)
            self.velocity.y = -400

        # directional stuff
        direc = self.facing.x
        if self._controller.up:
            # shoot a bit up
            shot_direction = self.facing.copy()
            shot_direction.y = -.4
            self.shoot(
                shot_direction
            )

            # recoil
            self.acceleration.x -= self._movement_acceleration * .7 * direc

        # run update from parent classes
        super().update(delta)

        self.image.blit(
            self._gun_image_right if direc >= 0 else self._gun_image_left,
            (
                5 * (direc),
                5
            )
        )

    @property
    def on_ground(self) -> bool:
        out = self.position.y + self.size.y / 2 > 900
        return out

    def shoot(
        self,
        direction: Vec2
    ) -> None:
        """
        shoot a bullet
        """
        # actual bullet
        Bullet(
            self.position + Vec2.from_cartesian(0, 7)
            + direction.normalize() * self.size.length * .4,
            direction.normalize() * 1300 + self.velocity
        )

        # casing
        casing_direction = direction.normalize()
        casing_direction.x *= -.3
        Bullet(
            self.position + Vec2.from_cartesian(0, 7)
            + casing_direction * self.size.length * .4,
            casing_direction * 500 + self.velocity,
            casing=True
        )
