"""
_effect.py
22. March 2024

a basic sound effect

Author:
Nilusink
"""
# from icecream import ic
from ._sounds import sounds
import typing as tp
import pygame as pg


class _SoundEffects:
    """
    a collection of all sound effects
    """
    def __init__(self) -> None:
        self._effects = []

    def add(self, effect: "SoundEffect") -> None:
        """
        add a sound effect to the queue
        """
        self._effects.append(effect)

    def remove(self, effect: "SoundEffect") -> None:
        """
        remove a sound effect from the queue
        """
        self._effects.remove(effect)

    def update(self) -> None:
        """
        update all sound effects
        """
        for effect in self._effects:
            effect.update()


sound_effects = _SoundEffects()


class SoundEffect:
    volume: float = 1

    def __new__(cls, *args, **kwargs):
        instance = super(SoundEffect, cls).__new__(cls)
        sound_effects.add(instance)
        return instance

    def __init__(
            self,
            sound_name: str,
            on_finish_playing: tp.Callable[[], None] = ...
    ) -> None:
        self._sound_name = sound_name
        self._sound: pg.mixer.Sound = ...
        self._playing: pg.mixer.Channel = ...
        self._on_finish = on_finish_playing
        self._last_playing = False

    @property
    def playing(self) -> bool:
        if self._playing is ...:
            return False

        return self._playing.get_busy()

    def play(
            self,
            loops: int = 0,
            maxtime: int = 0,
            fade_ms: int = 0,
    ) -> None:
        """
        play the sound effect
        """
        if self._sound is ...:
            self._sound = sounds.get_sound(self._sound_name)

            if self._sound is None:
                raise RuntimeError(f"Sound {self._sound_name} not found!")

        elif self.playing:
            self.stop()

        self._sound.set_volume(self.volume)
        tmp = self._sound.play(loops, maxtime, fade_ms)
        if tmp is None:
            return ...

        self._playing = tmp

    def stop(self) -> None:
        """
        stop the sound effect if it is currently playing
        """
        if self.playing:
            self._playing.stop()
            self._playing = ...

    def update(self) -> None:
        """
        updates called by the game loop
        """
        now = self.playing

        if self._last_playing and not now and self._on_finish is not ...:
            self._on_finish()

        self._last_playing = now


class PresetEffect(SoundEffect):
    _sound_name: str

    def __init__(self):
        super().__init__(self._sound_name)


class LargeExplosion(PresetEffect):
    _sound_name = "explosion_large"


class SmallExplosion(PresetEffect):
    _sound_name = "explosion_small"


class Shotgun(PresetEffect):
    _sound_name = "shotgun"


def sound_effect_wrapper(sound_name: str):
    return SoundEffect(sound_name)


class ThreeStageSoundEffect:
    _stage_one_name: str
    _stage_two_name: str
    _stage_three_name: str
    volume: float = 1

    def __init__(self) -> None:
        self._stage_three = SoundEffect(
            self._stage_three_name,
            self.stop
        )
        self._stage_three.volume = self.volume
        self._stage_two = SoundEffect(
            self._stage_two_name,
            self._play_3
        )
        self._stage_two.volume = self.volume
        self._stage_one = SoundEffect(
            self._stage_one_name,
            self._play_2
        )
        self._stage_one.volume = self.volume
        self._playing = True
        self.play()

    @property
    def playing(self) -> bool:
        return self._playing

    def play(self) -> None:
        """
        play the sound effect
        """
        self._stage_one.play()

    def _play_2(self) -> None:
        if self._playing:
            self._stage_two.play()

    def _play_3(self) -> None:
        if self._playing:
            self._stage_three.play()

    def stop(self) -> None:
        """
        stop the sound effect from playing
        """
        self._playing = False


class ContinuousSoundEffect(ThreeStageSoundEffect):
    def __init__(self) -> None:
        super().__init__()
        self._stage_two = SoundEffect(
            self._stage_two_name,
        )
        self._stage_two.volume = self.volume
        self._one_done = False

    @property
    def stage_one_done(self) -> bool:
        return self._one_done

    def _play_2(self) -> None:
        self._one_done = True

        if self._playing:
            self._stage_two.play(-1)

    def done(self) -> None:
        """
        stop stage 2 playing
        """
        self._stage_two.stop()

        if self.stage_one_done:
            if self._playing:
                self._play_3()

        else:
            self._playing = False

    def stop(self) -> None:
        self._playing = False
        self.done()


class Minigun(ContinuousSoundEffect):
    _stage_one_name = "spool_up"
    _stage_two_name = "burst"
    _stage_three_name = "spool_down"
    volume: float = .3
