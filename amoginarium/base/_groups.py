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


class _Bullets(pg.sprite.Group):
    ...


class _Updated(pg.sprite.Group):
    ...


class _Drawn(pg.sprite.Group):
    ...


class _Walls(pg.sprite.Group):
    ...


class _WallCollider(pg.sprite.Group):
    """
    requires:
    on_wall: bool
    """
    def collides_with(self, sprite) -> None:
        collides = False
        with suppress(AttributeError):
            for wall in Walls.sprites():
                sprite: tp.Any
                wall: tp.Any
                if all([
                    pg.sprite.collide_rect(sprite, wall),
                    wall.position.y <= sprite.position.y + sprite.size.y,
                    sprite.position.y + sprite.size.y <= wall.position.y + wall.size.y
                ]):
                    collides = True
        
        return collides


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

                # draw mag / reload bar
                mag_n, mag_v = sprite.get_mag_state(1000)
                now_len = (mag_n / 1000) * max_len
                pg.draw.rect(
                    surface,
                    (0, 0, 0, 128),
                    pg.Rect(
                        bar_start.x,
                        bar_start.y + 1.5 * bar_height,
                        max_len if now_len else 0,
                        bar_height
                    )
                )
                pg.draw.rect(
                    surface,
                    (155, 155, 255, 255),
                    pg.Rect(
                        bar_start.x,
                        bar_start.y + 1.5 * bar_height,
                        now_len,
                        bar_height
                    )
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


class _CollisionDestroyed(pg.sprite.Group):
    """
    required methods / variables
    damage: float (optional, use if collision should damage the other object)
    hp: float (optional, sprite should either have damage or hp (or both))
    hit(damage: float) -> None
    kill() -> None
    """
    def update(self) -> None:
        calculated: list[set] = []
        for sprite in CollisionDestroyed.sprites():
            with suppress(AttributeError):
                for other in self.sprites():
                    sprite: tp.Any
                    other: tp.Any
                    if all([
                        # self.size_collide(sprite, other),
                        pg.sprite.collide_rect(sprite, other),
                        not (sprite.parent is other or other.parent is sprite),
                        other.parent is not sprite.parent
                    ]):
                        if {sprite, other} not in calculated:
                            try:
                                dmg = other.damage

                            except AttributeError:
                                dmg = 0

                            hp = sprite.hp
                            sprite.hit(dmg)
                            if dmg != 0:
                                other.hit_someone(target_hp=hp)

                    calculated.append({sprite, other})

    @staticmethod
    def size_collide(sprite1, sprite2) -> bool:
        # check for the first sprite to be in the second
        collision_distance = sprite1.size.length + sprite2.size.length
        return (
            sprite1.position_center - sprite2.position_center
        ).length <= collision_distance

    @staticmethod
    def box_collide(sprite1, sprite2) -> tp.Iterator:
        sprite1_pos = sprite1.position
        sprite2_pos = sprite2.position
        sprite1_size = sprite1.size
        sprite2_size = sprite2.size

        sprite1_center = sprite1.position_center
        sprite2_center = sprite2.position_center

        return all([
            sprite1_pos.x < sprite2_center.x < sprite1_pos.x + sprite1_size.x,
            sprite1_pos.y < sprite2_center.y < sprite1_pos.y + sprite1_size.y
        ]) or all([
            sprite2_pos.x < sprite1_center.x < sprite2_pos.x + sprite2_size.x,
            sprite2_pos.y < sprite1_center.y < sprite2_pos.y + sprite2_size.y
        ])


# initialize groups
Drawn = _Drawn()
Walls = _Walls()
Bullets = _Bullets()
HasBars = _HasBars()
Updated = _Updated()
WallBouncer = _WallBouncer()
WallCollider = _WallCollider()
GravityAffected = _GravityAffected()
FrictionXAffected = _FrictionXAffected()
CollisionDestroyed = _CollisionDestroyed()
