"""
_basegame.py
25. January 2024

Defines the core game

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, sleep, strftime
from icecream import ic
import pygame as pg
import json

from ._groups import Updated, GravityAffected, Drawn, FrictionXAffected
from ..controllers import Controllers, Controller
from ..debugging import run_with_debug
from ..logic import SimpleLock
from ..entities import Player


def current_time() -> str:
    ms = str(round(perf_counter(), 4)).split(".")[1]
    return f"{strftime('%H:%M:%S')}.{ms: <4} |> "


class BaseGame:
    running: bool = True
    _last_logic: float

    def __init__(
                self,
                debug: bool = False
            ) -> None:
        # configure icecream
        if not debug:
            ic.disable()

        ic.configureOutput(prefix=self.time_since_start)

        self._pool = ThreadPoolExecutor(max_workers=5)

        # debugging
        self._logic_loop_times: list[tuple[float, float]] = []
        self._pygame_loop_times: list[tuple[float, float]] = []
        self._comms_loop_times: list[tuple[float, float]] = []

        self._pygame_fps: int = 0
        self._logic_fps: int = 0
        self._comms_ping: int = 0

        # logic setup
        self._new_controllers: list[Controller] = []
        self._new_controllers_lock = SimpleLock()

        self._controllers_cid = Controllers.on_new_controller(
            self._add_controller
        )

        # initialize pygame stuff
        pg.init()
        pg.font.init()

        screen_info = pg.display.Info()
        window_size = (screen_info.current_w, screen_info.current_h)

        self.screen = pg.display.set_mode(window_size, pg.SCALED)
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("amoginarium")

        # add decorator with callback to self.end
        for func in ("_run_pygame", "_run_logic", "_run_comms"):
            setattr(
                self,
                func,
                run_with_debug(
                    on_fail=lambda *_: self.end(),
                    reraise_errors=True
                )(getattr(self, func))
            )

        self._game_start = 0

    def time_since_start(self) -> str:
        """
        styleized time since game start
        gamestart being time since `mainloop` was called
        """
        return f"{round(perf_counter() - self._game_start, 4): >8} |> "

    def _add_controller(self, controller: Controller) -> None:
        """
        appends a new controller to the queue
        """
        self._new_controllers_lock.aquire()
        self._new_controllers.append(controller)
        self._new_controllers_lock.release()

    def _run_pygame(self) -> None:
        """
        start pygame
        """
        last = perf_counter()
        last_fps_print = 0
        while self.running:
            now = perf_counter()

            # only update fps every 200ms (for readability)
            if now - last_fps_print > .2:
                self._pygame_fps = int(1 / (now - last))
                last_fps_print = now

            # clear screen
            self.screen.fill((52, 189, 235, 255))
            self.lowest_layer.fill((0, 0, 0, 0))
            self.middle_layer.fill((0, 0, 0, 0))
            self.top_layer.fill((0, 0, 0, 0))

            # handle events
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        ic("pygame end")
                        return self.end()

            # handle groups
            Drawn.draw(self.middle_layer)

            # show fps
            fps_surf = self.font.render(
                f"{self._pygame_fps} FPS (render)", False, (255, 255, 255, 255)
            )
            self.top_layer.blit(fps_surf, (0, 0))
            fps_surf = self.font.render(
                f"{self._logic_fps} FPS (logic)", False, (255, 255, 255, 255)
            )
            self.top_layer.blit(fps_surf, (0, 15))
            ping_surf = self.font.render(
                f"{self._comms_ping} ms ping", False, (255, 255, 255, 255)
            )
            self.top_layer.blit(ping_surf, (0, 30))

            # draw layers
            self.screen.blit(self.lowest_layer, (0, 0))
            self.screen.blit(self.middle_layer, (0, 0))
            self.screen.blit(self.top_layer, (0, 0))

            pg.display.update()

            self._pygame_loop_times.append(
                (now - self._game_start, now - last)
            )
            last = now

        ic("pygame end")

    def _run_logic(self) -> None:
        """
        start game logic
        """
        last = perf_counter()
        last_fps_print = 0
        while self.running:
            now = perf_counter()

            # minimum loop time of .5 ms (so the CPU isn't stressed too much)
            while now - last < .0005:
                now = perf_counter()

            delta = now - last

            # only update fps every 200ms (for readability)
            if now - last_fps_print > .2:
                self._logic_fps = int(1 / delta)
                last_fps_print = now

            # check for new controllers
            if len(self._new_controllers) > 0:
                self._new_controllers_lock.aquire()
                tmp = self._new_controllers.copy()
                self._new_controllers.clear()
                self._new_controllers_lock.release()

                for new_controller in tmp:
                    # spawn new player
                    Player(controller=new_controller)
                    ic(new_controller, Player)

            # update entities
            GravityAffected.calculate_gravity(delta)
            FrictionXAffected.calculate_friction(delta)

            Updated.update(delta)

            self._logic_loop_times.append(
                (now - self._game_start, delta)
            )
            last = now

        ic("logic end")

    def _run_comms(self) -> None:
        """
        start communications
        """
        last = perf_counter()
        while self.running:
            now = perf_counter()
            delta = now - last

            sleep(.1)

            self._comms_ping = int(delta * 1000)
            self._comms_loop_times.append(
                (now - self._game_start, delta)
            )
            last = now

        ic("comms end")

    def mainloop(self) -> None:
        """
        run the game
        """
        self._game_start = perf_counter()

        self._pool.submit(self._run_logic)
        self._pool.submit(self._run_comms)
        self._run_pygame()

    @run_with_debug()
    def end(self) -> None:
        """
        stop everything
        """
        # tell threads to exit
        self.running = False

        ic("stopping game...")

        # quit pygame
        pg.quit()

        # write debug data
        ic("writing debug data")
        with open("debug.json", "w") as out:
            json.dump({
                "logic": self._logic_loop_times,
                "comms": self._comms_loop_times,
                "pygame": self._pygame_loop_times
            }, out)

        ic("done writing debug data")

        # stop threads
        ic("waiting for threads to quit...")
        self._pool.shutdown(wait=True)
        ic("all threads exited")
