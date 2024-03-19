"""
_static_turret.py
18. March 2024

defines a player

Author:
Nilusink
"""
from contextlib import suppress
# from icecream import ic
import typing as tp

from ..base import HasBars, CollisionDestroyed, Players, Updated
from ..base import GravityAffected
from ._weapons import BaseWeapon, Sniper, Ak47, Minigun, Mortar
from ..render_bindings import draw_circle, draw_dashed_circle
from ..logic import Vec2, calculate_launch_angle, Color
from ._base_entity import VisibleEntity


class BaseTurret(VisibleEntity):
    size: Vec2
    weapon: BaseWeapon
    _body_texture: int = ...
    _body_texture_path: str
    _weapon_texture: int | None = ...
    _weapon_texture_path: str | None
    _max_hp: int = 80
    _hp: int = 0
    _aim_type: tp.Literal["low", "high"] = "low"

    def __new__(cls, *args, **kwargs):
        # only load texture once
        if cls._body_texture is ...:
            cls.load_textures()

        return super(BaseTurret, cls).__new__(cls)

    @classmethod
    def load_textures(cls) -> None:
        return
        # cls._body_texture, _ = load_texture(
        #     cls._body_texture_path,
        #     (64, 64)
        # )
        # if cls._weapon_texture_path is not None:
        #     cls._weapon_texture, _ = load_texture(
        #         cls._weapon_texture_path,
        #         (64, 64)
        #     )

    def __init__(
        self,
        size: Vec2,
        position: Vec2,
        weapon: BaseWeapon,
        engagement_range: float
    ) -> None:
        self.weapon = weapon
        self.engagement_range = engagement_range

        self._hp = self._max_hp

        super().__init__(
            size=size,
            initial_position=position
        )

        self.add(CollisionDestroyed, HasBars)

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def hp(self) -> int:
        return self._hp

    def hit(self, damage: float) -> None:
        """
        deal damage to the turret
        """
        self._hp -= damage

        # check for turret death
        if self._hp <= 0:
            self.kill()

    def update(self, delta):
        # update weapon
        self.weapon.update(delta)

        # scan for players and engage the closest one
        players = Players.get_entities_in_circle(
            self.position,
            self.engagement_range
        )

        if len(players) > 0:
            _, closest_player = players[0]
            player_velocity = closest_player.velocity.copy()

            position_delta = closest_player.position - self.position
            position_delta.y *= -1
            player_velocity.y *= -1

            mirror = False
            if position_delta.x < 0:
                position_delta.x *= -1
                player_velocity.x *= -1
                mirror = True

            # try to predict where the player is going to be
            with suppress(ValueError):
                aiming_angle = calculate_launch_angle(
                    position_delta,
                    player_velocity,
                    self.weapon.bullet_speed,
                    4,
                    self._aim_type,
                    g=GravityAffected.gravity * 2
                )

                aiming_angle.y *= -1

                if mirror:
                    aiming_angle.x *= -1

                self.weapon.shoot(aiming_angle)

        super().update(delta)

    def gl_draw(self) -> None:
        # only draw if on screen
        if not any([
            Updated.world_position.x < self.position.x - self.size.x / 2,
            self.position.x + self.size.x / 2 < Updated.world_position.x+1920,
            Updated.world_position.y < self.position.y - self.size.y / 2,
            self.position.y + self.size.y / 2 < Updated.world_position.y+1080,
        ]):
            return

        # draw turret
        draw_circle(
            self.world_position,
            self.size.length / 2,
            16,
            Color.from_255(100, 100, 100)
        )

        # draw engagement ragne
        draw_dashed_circle(
            self.world_position,
            self.engagement_range,
            64,
            Color.white(),
            3
        )


class SniperTurret(BaseTurret):
    _max_hp: int = 40

    def __init__(self, position: Vec2) -> None:
        weapon = Sniper(self, True)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            2000
        )


class AkTurret(BaseTurret):
    _max_hp: int = 60

    def __init__(self, position: Vec2) -> None:
        weapon = Ak47(self, False)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            1200
        )


class MinigunTurret(BaseTurret):
    _max_hp: int = 60

    def __init__(self, position: Vec2) -> None:
        weapon = Minigun(self, False)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            1400
        )


class MortarTurret(BaseTurret):
    _max_hp: int = 80
    _aim_type = "high"

    def __init__(self, position: Vec2) -> None:
        weapon = Mortar(self, False)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            1000
        )
