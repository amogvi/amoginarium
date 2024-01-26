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


class _HasBars(pg.sprite.Group):
    """
    required methods / variables:
    hp: float
    max_hp: float
    """

    def draw(self, surface: pg.Surface) -> None:
        for sprite in self.sprites():
            with suppress(KeyError):
                sprite: tp.Any
                bar_height = sprite.size.y / 10

                # draw health bar
                max_len = sprite.size.x
                now_len = (sprite.hp / sprite.max_hp) * max_len

                bar_start = sprite.position.copy()
                bar_start.x -= sprite.size.x / 2
                bar_start.y += sprite.size.y / 2 + 10

                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(*bar_start.xy, max_len, bar_height)
                )
                pg.draw.rect(
                    surface,
                    (0, 255, 0, 255),
                    pg.Rect(*bar_start.xy, now_len, bar_height)
                )


class _WallBouncer(pg.sprite.Group):
    """
    required methods / variables:
    velocity: Vec2
    position: Vec2
    """
    def update(self) -> None:
        for sprite in self.sprites():
            with suppress(AttributeError):
                sprite: tp.Any
                if 10 > sprite.position.x:
                    sprite.velocity.x = abs(sprite.velocity.x)

                elif sprite.position.x > 1920:
                    print(sprite.position)
                    sprite.velocity.x = -abs(sprite.velocity.x)

                if 10 > sprite.position.y:
                    sprite.velocity.y = abs(sprite.velocity.y)

                elif sprite.position.y > 900:
                    sprite.velocity.y = -abs(sprite.velocity.y)


# initialize groups
Drawn = _Drawn()
HasBars = _HasBars()
Updated = _Updated()
WallBouncer = _WallBouncer()
GravityAffected = _GravityAffected()
FrictionXAffected = _FrictionXAffected()
