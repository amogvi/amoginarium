"""
_basegame.py
25. January 2024

Defines the core game

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, strftime
from icecream import ic
from contextlib import suppress
from pygame.locals import DOUBLEBUF, OPENGL
import pygame as pg
import asyncio
import json

from OpenGL.GL import glEnable, glClearColor, glBlendFunc
from OpenGL.GL import glMatrixMode, glLoadIdentity
from OpenGL.GL import GL_PROJECTION, GL_SRC_ALPHA
from OpenGL.GL import GL_BLEND
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GLU import gluOrtho2D

from ._groups import HasBars, WallBouncer, CollisionDestroyed, Bullets, Players
from ._groups import Updated, GravityAffected, Drawn, FrictionXAffected
from ..controllers import Controllers, Controller, GameController
from ._scrolling_background import ParalaxBackground
from ..debugging import run_with_debug
from ..entities import Player, Island
from ..communications import Server
from ..logic import SimpleLock
# from ..render_bindings import render_text


def current_time() -> str:
    ms = str(round(perf_counter(), 4)).split(".")[1]
    return f"{strftime('%H:%M:%S')}.{ms: <4} |> "


class BaseGame:
    running: bool = True
    _last_logic: float

    def __init__(
            self,
            debug: bool = False,
            game_port: int = 12345
    ) -> None:
        # configure icecream
        if not debug:
            ic.disable()

        ic.configureOutput(prefix=self.time_since_start)

        # multi-threading stuff
        self._pool = ThreadPoolExecutor(max_workers=5)

        # debugging
        self._logic_loop_times: list[tuple[float, float]] = []
        self._pygame_loop_times: list[tuple[float, float]] = []
        self._comms_loop_times: list[tuple[float, float]] = []

        # time since start, n_bullets, loop_time
        self._n_bullets_times: list[tuple[float, float, float]] = []

        self._pygame_fps: int = 0
        self._logic_fps: int = 0
        self._comms_ping: int = 0

        # logic setup
        self._new_controllers: list[Controller] = []
        self._new_controllers_lock = SimpleLock()

        self._controllers_cid = Controllers.on_new_controller(
            self._add_controller
        )

        # server setup
        self._server = Server(("0.0.0.0", game_port))

        # initialize pygame stuff
        pg.init()
        pg.font.init()

        screen_info = pg.display.Info()
        window_size = (screen_info.current_w, screen_info.current_h)

        self.screen = pg.display.set_mode(
            window_size,
            DOUBLEBUF | OPENGL | pg.RESIZABLE
        )
        self.lowest_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.middle_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.top_layer = pg.Surface(window_size, pg.SRCALPHA, 32)
        self.font = pg.font.SysFont(None, 24)
        pg.display.set_caption("amoginarium")

        # initialize OpenGL stuff
        glClearColor(*(0, 0, 0, 255))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, *window_size, 0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # initialize background
        self._background = ParalaxBackground(
            "assets/images/bg1",
            *window_size,
            parallax_multiplier=1.6
        )
        # rbg = randint(1, 4)
        # self._background = ScrollingBackground(
        #     "assets/images/bg1/layers/7.png",
        #     f"assets/images/bg{rbg}/bg.png",
        #     *window_size
        # )

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

        Island.random_between(
            100, 1800,
            500, 900,
            10, 1500,
            10, 20
        )
        self._game_start = 0

    def time_since_start(self) -> str:
        """
        styleized time since game start
        gamestart being time since `mainloop` was called
        """
        if hasattr(self, "_game_start"):
            t_ms = round(perf_counter() - self._game_start, 4)

        # if game hasn't started yet (bassegame init), set time to -1
        else:
            t_ms = -1.0

        t1, t2 = str(t_ms).split(".")
        return f"{t1: >4}.{t2: <4} |> "

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
        clock = pg.time.Clock()

        # draw background once
        while self.running:
            now = perf_counter()

            delta = now-last

            # only update fps every 200ms (for readability)
            if now - last_fps_print > .2:
                self._pygame_fps = int(1 / delta)
                last_fps_print = now

            # handle events
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        ic("pygame end")
                        return self.end()

                    case pg.JOYDEVICEADDED:
                        joy = pg.joystick.Joystick(event.device_index)
                        GameController(joy.get_guid(), joy)

            # update logic
            self._update_logic(delta, now)

            # clear screen
            glClearColor(*(0, 0, 0, 255))
            self.screen.fill((0, 0, 0, 0))
            self.middle_layer.fill((0, 0, 0, 0))
            self.top_layer.fill((0, 0, 0, 0))

            # draw background
            min_player_pos, max_player_pos = Players.get_position_extremes()

            background_pos_right = self._background.position\
                + self.screen.get_width() - 60
            background_pos_left = self._background.position + 60

            if max_player_pos.x > background_pos_right:
                self._background.scroll(delta * 5)
                Updated.world_position.x = self._background.position

            elif min_player_pos.x < background_pos_left:
                self._background.scroll(-delta * 5)
                Updated.world_position.x = self._background.position

            self._background.draw(self.lowest_layer)

            # handle groups
            Drawn.gl_draw()
            HasBars.gl_draw()

            # # show fps
            # fps_surf = self.font.render(
            #     f"{self._pygame_fps} FPS (render)", False, (255, 255, 255, 255)
            # )

            # self.top_layer.blit(fps_surf, (0, 0))
            # fps_surf = self.font.render(
            #     f"{self._logic_fps} FPS (logic)", False, (255, 255, 255, 255)
            # )
            # self.top_layer.blit(fps_surf, (0, 15))
            # ping_surf = self.font.render(
            #     f"{self._comms_ping} ms ping", False, (255, 255, 255, 255)
            # )
            # self.top_layer.blit(ping_surf, (0, 30))

            # render_text(
            #     f"{self._pygame_fps} FPS (render)",
            #     0, 0,
            #     self.font
            # )

            pg.display.flip()

            self._pygame_loop_times.append(
                (now - self._game_start, delta)
            )
            last = now

            clock.tick(60)

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

            self._update_logic(delta)

            last = now

        ic("logic end")

    def _update_logic(self, delta, now) -> None:
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
        WallBouncer.update()

        Updated.update(delta)

        CollisionDestroyed.update()

        self._logic_loop_times.append(
            (now - self._game_start, delta)
        )
        self._n_bullets_times.append(
            (now - self._game_start, len(Bullets.sprites()), delta)
        )

    def _run_comms(self) -> None:
        """
        start communications
        """
        asyncio.run(self._server.run())
        ic("comms end")
        return

    def mainloop(self) -> None:
        """
        run the game
        """
        self._game_start = perf_counter()

        # self._pool.submit(self._run_logic)
        # self._pool.submit(self._run_comms)
        self._run_pygame()

    @run_with_debug()
    def end(self) -> None:
        """
        stop everything
        """
        # check if end has already been called
        if not self.running:
            return

        # tell threads to exit
        self.running = False

        # tell server to shutdown
        with suppress(RuntimeError):
            self._server.close()

        ic("stopping game...")

        # quit pygame
        pg.quit()

        # write debug data
        ic("writing debug data")
        with open("debug.json", "w") as out:
            json.dump({
                "logic": self._logic_loop_times,
                "comms": self._comms_loop_times,
                "bullets": self._n_bullets_times,
                "pygame": self._pygame_loop_times
            }, out)

        ic("done writing debug data")

        # stop threads
        ic("waiting for threads to quit...")
        self._pool.shutdown(wait=True)
        ic("all threads exited")
