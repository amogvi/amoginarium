from random import randint
import pygame as pg


class BackgroundPlayer:
    def __init__(self) -> None:
        self._sound_files: list[pg.mixer.Sound] = []
        self._playing: pg.Channel = ...
        self.volume = 1

    def load_files(self, sound_files: list[str]) -> None:
        for file in sound_files:
            self._sound_files.append(pg.mixer.Sound(file))

    def start(self) -> None:
        sound = self._sound_files[
            randint(0, len(self._sound_files) - 1)
        ]
        sound.set_volume(self.volume)
        self._playing = sound.play(fade_ms=5000)

    def update(self) -> None:
        """
        checks if the sound is done and plays another one
        """
        if self._playing is ... or not self._playing.get_busy():
            self.start()
