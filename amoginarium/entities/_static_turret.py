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
from ..render_bindings import draw_textured_quad, draw_dashed_circle, load_texture
from ._weapons import BaseWeapon, Sniper, Ak47, Minigun, Mortar, Flak
from ..logic import Vec2, calculate_launch_angle, Color, is_related
from ._base_entity import VisibleEntity


class BaseTurret(VisibleEntity):
    size: Vec2
    weapon: BaseWeapon
    _body_texture: int = ...
    _body_texture_path: str
    _body_texture_path: str = "assets/images/static_turret_base.png"
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
        cls._body_texture, _ = load_texture(
            cls._body_texture_path,
            (64, 64)
        )
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
        engagement_range: float,
        airburst_munition: bool = False,
        intercept_bullets: bool = False
    ) -> None:
        self.weapon = weapon
        self.engagement_range = engagement_range
        self.airburst_munition = airburst_munition
        self.intercept_bullets = intercept_bullets

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

    def hit(self, damage: float, hit_by: tp.Self = ...) -> None:
        """
        deal damage to the turret
        """
        self._hp -= damage

        # check for turret death
        if self._hp <= 0:
            self.kill(hit_by)

    def update(self, delta):
        # update weapon
        self.weapon.update(delta)

        # scan for targets and engage the closest one
        targets = (
            CollisionDestroyed if self.intercept_bullets else Players
        ).get_entities_in_circle(
            self.position,
            self.engagement_range
        )

        # filter stuff shot by myself
        targets = [e for e in targets if not is_related(self, e[1])]

        if len(targets) > 0:
            _, closest_target = targets[0]
            player_velocity = closest_target.velocity.copy()

            position_delta = closest_target.position - self.position
            position_delta.y *= -1
            player_velocity.y *= -1

            mirror = False
            if position_delta.x < 0:
                position_delta.x *= -1
                player_velocity.x *= -1
                mirror = True

            # try to predict where the player is going to be
            with suppress(ValueError):
                aiming_angle, tof = calculate_launch_angle(
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

                # if airburst, explode at max engagement range
                tof = min(
                    tof,
                    self.engagement_range / self.weapon.bullet_speed
                )

                self.weapon.shoot(
                    aiming_angle,
                    tof if self.airburst_munition else ...
                )

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
        # draw_circle(
        #     self.world_position,
        #     self.size.length / 2,
        #     16,
        #     Color.from_255(100, 100, 100)
        # )
        draw_textured_quad(
            self._body_texture,
            *(self.world_position - self.size / 2).xy,
            *self.size.xy
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
            1000,
        )


class FlakTurret(BaseTurret):
    _max_hp: int = 80
    _aim_type = "low"

    def __init__(self, position: Vec2) -> None:
        weapon = Flak(self, True)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            1550,
            airburst_munition=True,
            intercept_bullets=False
        )
