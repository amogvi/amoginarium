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
from ._weapons import BaseWeapon, Sniper, Ak47, Minigun, Mortar, Flak
from ..logic import Vec2, calculate_launch_angle, Color, is_related
from ._base_entity import VisibleEntity
from ..render_bindings import renderer
from ..base._linked import global_vars
from ..base._textures import textures


class BaseTurret(VisibleEntity):
    size: Vec2
    weapon: BaseWeapon
    _body_texture: int = ...
    _body_texture_path: str
    _body_texture_path: str = "static_turret_base"
    _weapon_texture: int | None = ...
    _weapon_texture_path: str | None
    _max_hp: int = 80
    _hp: int = 0
    _aim_type: tp.Literal["low", "high"] = "low"
    _target: tp.Any = ...
    _target_predict: Vec2 = ...
    available_targets: dict = ...

    def __new__(cls, *args, **kwargs):
        # only load texture once
        if cls._body_texture is ...:
            cls.load_textures()

        return super(BaseTurret, cls).__new__(cls)

    @classmethod
    def load_textures(cls) -> None:
        if cls._body_texture is ...:
            cls._body_texture, _ = textures.get_texture(
                cls._body_texture_path,
                (64, 64)
            )

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
        self.available_targets = {}

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

    def get_next_target(self) -> tp.Any:
        """
        returns the next best target to shoot at
        """
        # ic(self.available_targets
        targets = list(self.available_targets.keys())
        for target in sorted(
            targets, key=lambda t: self.available_targets[t]["distance"]
        ):
            t = self.available_targets[target]
            if t["shot_at"] < 0:
                return target

        # all targets have been shot at, so shoot at nothing
        # and reset shot_ats
        for target in self.available_targets:
            self.available_targets[target]["shot_at"] = -1

        return None

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
        # targets = []

        for target in targets:
            if target[1] not in self.available_targets:
                self.available_targets[target[1]] = {
                    "shot_at": -1,
                    "distance": target[0]
                }

        # make list only contain the entities
        targets = [value[1] for value in targets]
        for target in self.available_targets.copy():
            if target not in targets:
                self.available_targets.pop(target)
                continue

            if self.available_targets[target]["shot_at"] >= -1:
                self.available_targets[target]["shot_at"] -= delta

        new_target = self.get_next_target()
        # ic(new_target)
        if new_target is not None:
            player_velocity = new_target.velocity.copy()
            player_acceleration = new_target.acceleration.copy()

            self._target = new_target

            # if target is on ground, subtrac gravitaional acceleration
            if hasattr(new_target, "on_ground"):
                if new_target.on_ground:
                    player_acceleration.y -= GravityAffected.gravity

            position_delta = new_target.position - self.position
            position_delta.y *= -1
            player_velocity.y *= -1
            player_acceleration.y *= -1

            mirror = False
            if position_delta.x < 0:
                position_delta.x *= -1
                player_velocity.x *= -1
                player_acceleration.x *= -1
                mirror = True

            # try to predict where the player is going to be
            self._target_predict = ...
            with suppress(ValueError):
                magic = player_velocity.length > self.weapon._bullet_speed

                aiming_angle, tof, predict = calculate_launch_angle(
                    position_delta,
                    player_velocity * .9 if magic else player_velocity,
                    player_acceleration,
                    self.weapon.bullet_speed,
                    10,
                    self._aim_type,
                    # *2 because for some reaseon I gave bullets 2x gravity
                    g=GravityAffected.gravity * 2
                )

                aiming_angle.y *= -1
                predict.y *= -1

                if mirror:
                    aiming_angle.x *= -1
                    predict.x *= -1

                self._target_predict = self.position + predict

                # if airburst, explode at max engagement range
                # idk why, but if engaging bullets, the tof is wrong and
                # x1.1 corrects it soemehow
                tof = min(
                    tof * 1.1 if magic else tof,
                    self.engagement_range / self.weapon.bullet_speed
                )

                shot = self.weapon.shoot(
                    aiming_angle,
                    tof if self.airburst_munition else ...,
                    target_pos=self._target_predict
                )

                if shot:
                    self.available_targets[new_target]["shot_at"] = \
                        self.weapon._reload_time

        else:
            self._target = ...
            self._target_predict = ...

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

        renderer.draw_textured_quad(
            self._body_texture,
            self.world_position - self.size / 2,
            self.size.xy
        )

        # draw engagement ragne
        renderer.draw_dashed_circle(
            self.world_position,
            self.engagement_range,
            64,
            Color.white(),
            3
        )

        # targets
        if global_vars.show_targets:
            if self._target is not ...:
                renderer.draw_line(
                    self.world_position,
                    self._target.world_position,
                    Color.from_255(255, 0, 0, 100)
                )
                renderer.draw_circle(
                    self._target.world_position,
                    global_vars.translate_scale(self._target.size.length / 2),
                    32,
                    Color.from_255(255, 0, 0, 100)
                )

            if self._target_predict is not ...:
                renderer.draw_line(
                    self.world_position,
                    global_vars.translate_screen_coord(self._target_predict),
                    Color.from_255(50, 200, 0, 100)
                )
                renderer.draw_circle(
                    global_vars.translate_screen_coord(self._target_predict),
                    global_vars.translate_scale(32),
                    32,
                    Color.from_255(50, 200, 0, 100)
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
            2400
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
            1500
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
            1200
        )


class MortarTurret(BaseTurret):
    _max_hp: int = 90
    _aim_type = "high"

    def __init__(self, position: Vec2) -> None:
        weapon = Mortar(self, False)
        weapon.reload(True)

        super().__init__(
            Vec2.from_cartesian(64, 64),
            position,
            weapon,
            1800,
        )


class FlakTurret(BaseTurret):
    _max_hp: int = 70
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
