"""
_player.py
26. January 2024

defines a player

Author:
Nilusink
"""
from time import perf_counter
import typing as tp

from ..base import GravityAffected, FrictionXAffected, HasBars
from ..base import CollisionDestroyed, WallCollider, Players
from ._base_entity import LRImageEntity
from ._weapons import Minigun as Weapon
from ..render_bindings import renderer
from ..base._textures import textures
from ..controllers import Controller
from ..logic import Vec2


PLAYER_RIGHT_64_PATH = "gunogus64right"
PLAYER_OOB_RIGHT_64_PATH = "amogusOOB64right"
PLAYER_OOB_LEFT_64_PATH = "amogusOOB64left"


class Player(LRImageEntity):
    _player_right_64_texture: int = ...
    _player_left_64_texture: int = ...
    _player_oob_right_1_texture: int = ...
    _player_oob_right_2_texture: int = ...
    _player_oob_left_1_texture: int = ...
    _player_oob_left_2_texture: int = ...
    _movement_acceleration: float = 700
    _heal_per_second: float = 1.5
    _time_to_heal: float = 10
    _max_hp: int = 80
    _hp: int = 0

    on_wall: bool = False

    def __new__(cls, *args, **kwargs):
        # only load texture once
        if cls._player_left_64_texture is ...:
            cls.load_textures()

        return super(Player, cls).__new__(cls)

    @classmethod
    def load_textures(cls) -> None:
        cls._player_right_64_texture, _ = textures.get_texture(
            PLAYER_RIGHT_64_PATH,
            (128, 64)
        )
        cls._player_left_64_texture, _ = textures.get_texture(
            PLAYER_RIGHT_64_PATH,
            (128, 64),
            mirror="x"
        )

        cls._player_oob_right_1_texture, _ = textures.get_texture(
            PLAYER_OOB_RIGHT_64_PATH,
            (64, 64),
            mirror="x"
        )
        cls._player_oob_right_2_texture, _ = textures.get_texture(
            PLAYER_OOB_LEFT_64_PATH,
            (64, 64),
            mirror="x"
        )
        cls._player_oob_left_1_texture, _ = textures.get_texture(
            PLAYER_OOB_RIGHT_64_PATH,
            (64, 64),
        )
        cls._player_oob_left_2_texture, _ = textures.get_texture(
            PLAYER_OOB_LEFT_64_PATH,
            (64, 64),
        )

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

        if initial_position is ...:
            initial_position = Players.spawn_point

        # load textures
        if size == 64:
            self._texture_right = self._player_right_64_texture
            self._texture_left = self._player_left_64_texture

        else:
            self._texture_right, _ = textures.get_texture(
                PLAYER_RIGHT_64_PATH,
                (size * 2, size)
            )
            self._texture_left, _ = textures.get_texture(
                PLAYER_RIGHT_64_PATH,
                (size * 2, size),
                mirror="x"
            )
        self._image_size = size

        super().__init__(
            size=Vec2.from_cartesian(size*2, size),
            facing=facing,
            initial_position=initial_position,
            initial_velocity=initial_velocity,
        )

        self.add(
            CollisionDestroyed,
            FrictionXAffected,
            GravityAffected,
            WallCollider,
            Players,
            HasBars
        )

        self.weapon = Weapon(self, False)
        self.weapon.reload()

        self._n_hits = 0

        self._last_hit = perf_counter()

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def on_ground(self) -> bool:
        if self._controller.joy_y < 0:
            return False

        return WallCollider.on_ground(
            self,
            alt_pos=(
                self.position.x,
                self.position.y + (self.size.y / 2 - 10)
            ),
            alt_size=(
                self.size.x / 4,
                10
            )
        )

    @property
    def parent(self) -> tp.Self:
        return self

    def hit(self, damage: float, hit_by: tp.Self = ...) -> None:
        """
        deal damage to the player
        """
        self._hp -= damage

        # check for player death
        if self._hp <= 0:
            self.kill(hit_by)

        # update last hit
        self._last_hit = perf_counter()

    def update(self, delta):
        # update reloads
        self.weapon.update(delta)

        # stay onground if touching ground
        if self.on_ground:
            self.velocity.y = -1
            self.acceleration.y = 0

        # update controls
        self._controller.update(delta)
        if self._controller.joy_x > 0:
            self.acceleration.x += self._movement_acceleration
            self.facing.x = 1

        elif self._controller.joy_x < 0:
            self.acceleration.x -= self._movement_acceleration
            self.facing.x = -1

        if self._controller.jump and self.on_ground:
            self._controller.rumble(300, 2000, 500)
            self.velocity.y = -400

        if self._controller.reload:
            self.weapon.reload()

        # directional stuff
        if self._controller.shoot:
            # shoot a bit up
            shot_direction = self.facing.copy()
            shot_direction.y = -.4
            self.weapon.shoot(
                shot_direction
            )

        # heal
        if self._hp < self._max_hp:
            if perf_counter() - self._last_hit > self._time_to_heal:
                self._hp += self._heal_per_second * delta

        # run update from parent classes
        super().update(delta)

    def gl_draw(self) -> None:
        # check if out of bounds
        # left of screen
        if self.world_position.x < 0:

            # facing
            if self.facing.x > 0:
                renderer.draw_textured_quad(
                    self._player_oob_left_2_texture,
                    (0, self.world_position.y),
                    (64, 64)
                )
            else:
                renderer.draw_textured_quad(
                    self._player_oob_left_1_texture,
                    (0, self.world_position.y),
                    (64, 64)
                )
            return

        # right of screen
        elif self.world_position.x > 1920:

            # facing
            if self.facing.x > 0:
                renderer.draw_textured_quad(
                    self._player_oob_right_1_texture,
                    (1920 - 64, self.world_position.y),
                    (64, 64)
                )
            else:
                renderer.draw_textured_quad(
                    self._player_oob_right_2_texture,
                    (1920 - 64, self.world_position.y),
                    (64, 64)
                )
            return

        super().gl_draw()
