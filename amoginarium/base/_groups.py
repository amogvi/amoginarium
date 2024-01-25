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


class _GravityAffected(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def calculate_gravity(self, _delta: float) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                if not sprite.on_ground or sprite.velocity.y < 0:
                    sprite.acceleration.y = 9.81
                    continue

                while sprite.on_ground:
                    sprite.position.y -= 0.01
                sprite.position.y += 0.01

                sprite.velocity.y = 0


# initialize groups
Updated = _Updated()
GravityAffected = _GravityAffected()
