"""
_base_entity.py
25. January 2024

defines the most basic form of an entity

Author:
Nilusink
"""
from OpenGL.GL import glRotated
# from icecream import ic
import pygame as pg
import typing as tp
import math as m

# from ..base._linked import global_vars
from ..render_bindings import renderer
from ..base import Updated, Drawn
from ..logic import Vec2


_next_entity_id = 0


class Entity(pg.sprite.Sprite):
    facing: Vec2
    position: Vec2
    velocity: Vec2
    acceleration: Vec2

    def __init__(
        self,
        size: Vec2 = ...,
        facing: Vec2 = ...,
        initial_position: Vec2 = ...,
        initial_velocity: Vec2 = ...,
        coalition: tp.Any = ...
    ) -> None:
        global _next_entity_id

        # assign unique id
        self.__id = _next_entity_id
        _next_entity_id += 1

        self._coalition = coalition

        self.size = Vec2.from_cartesian(1, 1) if size is ... else size
        self.facing = Vec2.from_cartesian(1, 0) if facing is ... else facing
        self.position = Vec2() if initial_position is ... else initial_position
        self.velocity = Vec2() if initial_velocity is ... else initial_velocity
        self.acceleration = Vec2()

        super().__init__()

        self.update_rect()
        self._generate_collision_mask()
        self.add(Updated)

    @property
    def id(self) -> int:
        """
        unique entity id (simplifies comparison)
        """
        return self.__id

    @property
    def position_center(self) -> Vec2:
        """
        return the center of the sprite
        """
        return self.position + self.size / 2

    @property
    def world_position(self) -> Vec2:
        """
        return the position relative to the world center
        """
        return self.position - Updated.world_position

    @property
    def is_bullet(self) -> bool:
        return False

    @property
    def root(self):
        """
        get the root entity
        """
        return self._parent.root

    @property
    def coalition(self) -> tp.Any:
        return self._coalition

    def _generate_collision_mask(self) -> None:
        """
        generate the mask used for precise collision
        """
        self.mask = pg.mask.Mask(self.size.xy, True)

    def on_ground(self) -> bool:
        return self.position.y + self.size.y > 1080

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )

    def update(self, delta: float) -> None:
        # update velocity and position
        self.velocity += self.acceleration * delta
        self.position += self.velocity * delta

        # re-calculate pygame stuff
        self.last_angle = self.velocity.angle

        self.update_rect()

    def kill(self, killed_by: tp.Self = ...) -> None:
        super().kill()


class VisibleEntity(Entity):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add(Drawn)

    def update_rect(self) -> None:
        self.rect = pg.Rect(
            self.position.x - self.size.x / 2,
            self.position.y - self.size.y / 2,
            self.size.x,
            self.size.y
        )

    def gl_draw(self) -> None:
        raise NotImplementedError(
            f"gl_draw wasn't implemented for \"{self.__class__.__name__}\""
        )


class ImageEntity(VisibleEntity):
    _original_image: pg.surface.Surface

    def __init__(self, texture_id: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._texture_id = texture_id

    def update(self, delta: float) -> None:
        super().update(delta)

    def gl_draw(self) -> None:
        glRotated(-self.velocity.angle * (180 / m.pi), 0, 0, 1)
        renderer.draw_textured_quad(
            self._texture_id,
            (
                self.rect.x - Updated.world_position.x,
                self.rect.y - Updated.world_position.y
            ),
            (
                self.size.x,
                self.size.y
            )
        )


class LRImageEntity(VisibleEntity):
    _texture_left: int
    _texture_right: int

    def __init__(self, *args, **kwargs) -> None:
        # self.image = self._image_right.copy()

        super().__init__(*args, **kwargs)

    def update(self, delta: float) -> None:
        # if self.facing.x > 0:
        #     self.image = self._image_right.copy()

        # elif self.facing.x < 0:
        #     self.image = self._image_left.copy()

        super().update(delta)

    def gl_draw(self) -> None:
        renderer.draw_textured_quad(
            self._texture_right if self.facing.x < 0 else self._texture_left,
            self.world_position - self.size / 2,
            self.size
        )
