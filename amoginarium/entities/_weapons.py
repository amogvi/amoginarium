"""
_weapons.py
26. January 2024

minigun go brrrrrt

Author:
Nilusink
"""
from time import perf_counter
from random import randint
# from icecream import ic

from ..base import GravityAffected, CollisionDestroyed, Bullets, Updated, Drawn
from ..render_bindings import load_texture, draw_circle
from ._base_entity import ImageEntity, Entity
from ..logic import Vec2, Color
from ..base import WallCollider


BULLET_PATH = "assets/images/bullet.png"


class Bullet(ImageEntity):
    _image_path: str = BULLET_PATH
    _bullet_texture: int = ...
    _base_damage: float = 1

    def __new__(cls, *args, **kwargs) -> None:
        # only load texture once
        if cls._bullet_texture is ...:
            cls.load_textures()

        return super(Bullet, cls).__new__(cls)

    @classmethod
    def load_textures(cls) -> None:
        cls._bullet_texture, _ = load_texture(BULLET_PATH, (10, 10))

    def __init__(
        self,
        parent: Entity,
        initial_position: Vec2,
        initial_velocity: Vec2,
        base_damage: float = 1,
        casing: bool = False,
        time_to_life: float = 2,
        size: int = 10
    ) -> None:
        size = Vec2.from_cartesian(size, size)
        self._casing = casing
        self._parent = parent
        self._base_damage = base_damage
        self._ttl = time_to_life
        self._initial_velocity = initial_velocity

        texture_id = self._bullet_texture

        self._start_time = perf_counter()

        super().__init__(
            texture_id=texture_id,
            size=size,
            initial_position=initial_position.copy(),
            initial_velocity=initial_velocity.copy()
        )

        self.add(GravityAffected)

        if not casing:
            self.add(Bullets, CollisionDestroyed)

    @property
    def on_ground(self) -> bool:
        return self.position.y > 1000 or WallCollider.collides_with(self)

    @property
    def damage(self) -> float:
        """
        get bullet damage
        """
        if self._casing:
            return 0

        # calculate damage based on base_damage and velocity
        speed_mult = 1 + (
            (self.velocity.length - 1300) / self._initial_velocity.length
        ) * .5
        damage = self._base_damage * speed_mult

        # ic(damage)

        return damage

    @property
    def parent(self) -> Entity:
        return self._parent

    def hit(self, _damage: float) -> None:
        self.kill()

    def hit_someone(self, target_hp: float) -> None:
        self.kill()

    def update(self, delta):
        if any([
            self.position.y > 1100,
            self.position.x < Updated.world_position.x - 2000,
            self.position.x > Updated.world_position.x + 4000,
            perf_counter() - self._start_time > self._ttl,
            self.on_ground
        ]):
            self.kill()
            return

        # double gravity (because why not)
        self.acceleration.y *= 2

        super().update(delta)

    def kill(self) -> None:
        if all([
            self._casing,
            not Updated.out_of_bounds_x(self)
        ]):
            self.position.y -= self.size.y / 2
            self.remove(
                Updated,
                CollisionDestroyed,
                GravityAffected
            )
            return

        self.remove(Drawn)

        super().kill()

    def gl_draw(self) -> None:
        if not self._casing:
            draw_circle(
                self.world_position,
                self.size.x * .4,
                5,
                Color.from_255(255, 255, 60)
            )
            return

        return super().gl_draw()


class BaseWeapon:
    _current_recoil_time: float = 0
    _current_reload_time: float = 0
    _mag_state: int = 0
    _recoil_factor: float
    _bullet_speed: float
    _recoil_time: float
    _reload_time: float
    _mag_size: int

    def __init__(
        self,
        parent,
        reload_time: float,
        recoil_time: float,
        recoil_factor: float,
        mag_size: int,
        inacuracy: float,
        bullet_speed: float,
        bullet_size: int = 10,
        bullet_damage: float = 1,
        drop_casings: bool = False,
    ) -> None:
        self.parent = parent
        self._mag_size = mag_size
        self._inacuracy = inacuracy
        self._reload_time = reload_time
        self._recoil_time = recoil_time
        self._reload_time = reload_time
        self._bullet_speed = bullet_speed
        self._drop_casings = drop_casings
        self._recoil_factor = recoil_factor
        self._bullet_damage = bullet_damage
        self._bullet_size = bullet_size

    @property
    def mag_size(self) -> int:
        return self.mag_size

    @property
    def recoil_factor(self) -> float:
        return self.recoil_factor

    @property
    def bullet_speed(self) -> float:
        return self._bullet_speed

    def get_mag_state(self, max_out: float) -> float:
        """
        returns the current mag size (rising when reloading)
        :param max_out: output size
        :returns: x out of max_out, value of current state
        """
        if not self._current_reload_time:
            return self._mag_state * (
                max_out / self._mag_size
            ), self._mag_state

        return (
            (
                (
                    self._reload_time-self._current_reload_time
                ) / self._reload_time
            ) * max_out,
            round(self._current_reload_time, 2)
        )

    def update(self, delta: float) -> None:
        """
        update weapon state (like reloading, ...)
        """
        # reload time
        if self._current_reload_time > 0:
            self._current_reload_time -= delta

        if self._current_reload_time < 0 and self._mag_state <= 0:
            self._current_reload_time = 0
            self._mag_state = self._mag_size

        # recoil time
        if self._current_recoil_time > 0:
            self._current_recoil_time -= delta

        if self._current_recoil_time < 0:
            self._current_recoil_time = 0

    def shoot(
        self,
        direction: Vec2
    ) -> None:
        """
        shoot a bullet and check for recoil and reload
        """
        # check if mag is empty
        if self._mag_state <= 0:
            if self._current_reload_time == 0:
                self._current_reload_time = self._reload_time

            return

        if self._current_recoil_time > 0:
            return

        # inacuracy
        offset = randint(-255, 255) / 255
        offset *= self._inacuracy
        direction.angle += offset

        # recoil
        if hasattr(self.parent, "_movement_acceleration"):
            recoil = direction * self.parent._movement_acceleration
            recoil *= self._recoil_factor
            self.parent.acceleration -= recoil

        self._current_recoil_time = self._recoil_time

        self._mag_state -= 1

        # actual bullet
        Bullet(
            self.parent,
            self.parent.position + Vec2.from_cartesian(0, 7)
            + direction.normalize() * self.parent.size.length * .45,
            direction.normalize() * self._bullet_speed + self.parent.velocity,
            base_damage=self._bullet_damage,
            size=self._bullet_size
        )

        if self._drop_casings:
            # casing
            casing_direction = direction.normalize()
            casing_direction.x *= -.3
            Bullet(
                self.parent,
                self.parent.position + Vec2.from_cartesian(0, 7)
                + casing_direction * self.parent.size.length * .4,
                casing_direction * 500 + self.parent.velocity,
                casing=True
            )

    def reload(self, instant: bool = False) -> None:
        """
        reload the weapon
        """
        self._mag_state = 0
        self._current_reload_time = .1 if instant else self._reload_time


class Minigun(BaseWeapon):
    def __init__(self, parent, drop_casings: bool = False) -> None:
        super().__init__(
            parent,
            reload_time=3,
            recoil_time=.02,
            recoil_factor=2,
            mag_size=80,
            inacuracy=.01093606,
            bullet_speed=1300,
            bullet_damage=2,
            drop_casings=drop_casings
        )


class Ak47(BaseWeapon):
    def __init__(self, parent, drop_casings: bool = False) -> None:
        super().__init__(
            parent,
            reload_time=2.5,
            recoil_time=.1,
            recoil_factor=1,
            mag_size=30,
            inacuracy=0.03,
            bullet_size=11,
            bullet_speed=1200,
            bullet_damage=2.5,
            drop_casings=drop_casings
        )


class Sniper(BaseWeapon):
    def __init__(self, parent, drop_casings: bool = False) -> None:
        super().__init__(
            parent,
            reload_time=5,
            recoil_time=2,
            recoil_factor=50,
            mag_size=6,
            inacuracy=.00500002,
            bullet_size=15,
            bullet_speed=2500,
            bullet_damage=10,
            drop_casings=drop_casings
        )
