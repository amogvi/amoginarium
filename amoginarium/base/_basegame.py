"""
_basegame.py
25. January 2024

Defines the core game

Author:
Nilusink
"""
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter, strftime
from contextlib import suppress
from icecream import ic
import typing as tp
import pygame as pg
import asyncio
import json
import os

from OpenGL.GL import glClearColor

from ._groups import HasBars, WallBouncer, CollisionDestroyed, Bullets, Players
from ._groups import Updated, GravityAffected, Drawn, FrictionXAffected
from ..controllers import Controllers, Controller, GameController
from ..entities import Player, Island, Bullet, BaseTurret
from ._scrolling_background import ParalaxBackground
from ..logic import SimpleLock, Color, Vec2
from ..debugging import run_with_debug
from ..render_bindings import renderer
from ..communications import Server
from ..animations import explosion
from ._linked import global_vars
from ._textures import textures


class BoundFunction(tp.TypedDict):
    func: tp.Callable
    args: tuple
    kwargs: dict


def current_time() -> str:
    ms = str(round(perf_counter(), 4)).split(".")[1]
    return f"{strftime('%H:%M:%S')}.{ms: <4} |> "


class BaseGame:
    running: bool = True
    _last_logic: float
    _bg_color: tuple[float, float, float]
    _instance: tp.Self = ...

    def __new__(cls, *args, **kwargs) -> "BaseGame":
        # only one instance can exist
        if cls._instance is not ...:
            return cls._instance

        new = super(BaseGame, cls).__new__(cls)
        cls._instance = new
        return new

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
        self._total_loop_times: list[tuple[float, float]] = []

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

        # other things
        # self._in_next_loop: list[BoundFunction] = []

        # server setup
        self._server = Server(("0.0.0.0", game_port))

        # initialize pygame (logic) and renderer
        pg.init()
        renderer.init("amoginarium")

        # initialize background
        self._background = ...

        # add decorator with callback to self.end
        for func in ("_run_pygame", "_run_logic", "_run_comms"):
            setattr(
                self,
                func,
                run_with_debug(
                    on_fail=lambda *_: self.end(),
                    reraise_errors=False
                )(getattr(self, func))
            )

        self._background = ParalaxBackground(
            "bg1_layers",
            *global_vars.screen_size.xy,
            parallax_multiplier=1.6
        )

        # load map
        self.preload()
        self.load_map("assets/maps/test.json")

        self._game_start = 0

    @run_with_debug(reraise_errors=True, show_finish=True)
    def preload(self) -> None:
        """
        load all textures n stuff
        """
        # load entity textures
        textures.load_images("assets/images/textures.zip")
        textures.load_images("assets/images/bg1/bg1_layers.zip")
        textures.load_images("assets/images/animations/explosion.zip")

        self._background.load_textures()
        Island.load_textures()
        Player.load_textures()
        Bullet.load_textures()
        BaseTurret.load_textures()
        explosion.load_textures(size=(512, 512))

    def load_map(self, map_path: tp.LiteralString) -> None:
        """
        load a map from a json file
        """
        if not os.path.isfile(map_path):
            # if the file wasn't found, try adding the root program path
            map_path = os.path.dirname(__file__) + "/" + map_path
            ic(map_path)
            if not os.path.isfile(map_path):
                raise FileNotFoundError(f"Couldn't find map \"{map_path}\"")

        # load map data
        data = json.load(open(map_path, "r"))

        pg.display.set_caption(f"amoginarium - {data["name"]}")
        self._bg_color = Color.to_1(*data["background"])
        Players.spawn_point = Vec2.from_cartesian(*data["spawn_pos"])

        # load islands
        for island in data["platforms"]:
            Island(
                Vec2.from_cartesian(*island["pos"]),
                Vec2.from_cartesian(*island["size"]),
                island["texture"]
            )

        # load entities

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

    def run_in_next_loop[**A, R](
            self,
            func: tp.Callable[A, R],
            *args: A.args,
            **kwargs: A.kwargs
    ) -> None:
        global_vars.in_next_loop.append({
            "func": func,
            "args": args,
            "kwargs": kwargs
        })

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
            # total delta since last call
            now = perf_counter()
            delta = now-last

            # update logic
            self._update_logic(delta, now)

            # pygame loop time
            start = perf_counter()

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

            # clear screen
            glClearColor(0, 0, 0, 1)
            # self.screen.fill((0, 0, 0, 0))
            # self.middle_layer.fill((0, 0, 0, 0))
            # self.top_layer.fill((0, 0, 0, 0))

            min_player_pos, max_player_pos = Players.get_position_extremes()

            background_pos_right = self._background.position\
                + global_vars.screen_size.x - 60
            background_pos_left = self._background.position + 60

            if max_player_pos.x > background_pos_right:
                self._background.scroll(delta * 15)
                Updated.world_position.x = self._background.position

            elif min_player_pos.x < background_pos_left:
                self._background.scroll(-delta * 15)
                Updated.world_position.x = self._background.position

            # global_vars.pixel_per_meter *= .9995

            # draw background
            self._background.draw()

            # handle groups
            Drawn.gl_draw()
            HasBars.gl_draw()

            # draw in_loop
            for f in [*global_vars.in_next_loop, *global_vars.get_in_loop()]:
                f["func"](*f["args"], **f["kwargs"])

            global_vars.in_next_loop.clear()

            # # show fps
            # fps_surf = self.font.render(
            #     f"{self._pygame_fps} FPS (render)", False, (255, 255, 255,
            # 255)
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
                (now - self._game_start, perf_counter() - start)
            )
            self._total_loop_times.append(
                (now - self._game_start, delta)
            )
            last = now

            clock.tick(global_vars.max_fps)

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

            self._update_logic(delta, now)

            last = now

        ic("logic end")

    def _update_logic(self, delta, now) -> float:
        start = perf_counter()

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

        logic_time = perf_counter() - start
        self._logic_loop_times.append(
            (now - self._game_start, logic_time)
        )
        self._n_bullets_times.append(
            (now - self._game_start, len(Bullets.sprites()), logic_time)
        )

        return logic_time

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
                "pygame": self._pygame_loop_times,
                "total": self._total_loop_times
            }, out)

        ic("done writing debug data")

        # stop threads
        ic("waiting for threads to quit...")
        self._pool.shutdown(wait=True)
        ic("all threads exited")
