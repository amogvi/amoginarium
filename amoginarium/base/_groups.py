"""
_groups.py
25. January 2024

Defines sprite groups

Author:
Nilusink
"""
from contextlib import suppress
import pygame as pg
import typing as tp


class _Updated(pg.sprite.Group):
    ...


class _Drawn(pg.sprite.Group):
    ...


class _GravityAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def calculate_gravity(self, _delta: float) -> None:
        for sprite in self.sprites():
            sprite: tp.Any

            sprite.acceleration.y = 9.81 * 50

            with suppress(AttributeError):
                if sprite.on_ground:
                    while sprite.on_ground:
                        sprite.position.y -= 0.01

                    sprite.position.y += 0.01
                    sprite.velocity.y = 0


class _FrictionXAffected(pg.sprite.Group):
    def calculate_friction(self, delta: float) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite.acceleration.x = 0
                sprite: tp.Any
                sprite.velocity.x *= 1 - (0.5 * delta)


# initialize groups
Drawn = _Drawn()
Updated = _Updated()
GravityAffected = _GravityAffected()
FrictionXAffected = _FrictionXAffected()
