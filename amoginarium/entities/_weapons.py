"""
_weapons.py
26. January 2024

minigun go brrrrrt

Author:
Nilusink
"""
from time import perf_counter

from ..base import GravityAffected, CollisionDestroyed, Bullets, Updated, Drawn
from ..render_bindings import load_texture, draw_circle
from ._base_entity import ImageEntity, Entity
from ..base import WallCollider
from ..logic import Vec2


BULLET_PATH = "assets/images/bullet.png"


class Bullet(ImageEntity):
    _image_path: str = BULLET_PATH
    _bullet_texture: int = ...
    _damage: float = 1

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
        casing: bool = False
    ) -> None:
        size = Vec2.from_cartesian(10, 10)
        self._casing = casing
        self._parent = parent

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
        return self._damage if not self._casing else 0

    @property
    def parent(self) -> Entity:
        return self._parent

    def hit(self, _damage: float) -> None:
        self.kill()

    def hit_someone(self, target_hp: float) -> None:
        self.kill()

    def update(self, delta):
        if any([
            self.position.y > 1000,
            self.position.x < Updated.world_position.x,
            self.position.x > Updated.world_position.x + 2000,
            perf_counter() - self._start_time > 2,
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
                (163 / 255, 157 / 255, 116 / 255)
            )
            return

        return super().gl_draw()
