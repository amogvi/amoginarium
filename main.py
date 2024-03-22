#! venv/bin/python
from amoginarium.controllers import KeyboardController
from amoginarium.base import BaseGame
from amoginarium.entities import SniperTurret, AkTurret, MinigunTurret, MortarTurret, FlakTurret
from amoginarium.logic import Vec2


def main():
    game = BaseGame(debug=True)

    # create initial controller
    KeyboardController()
    # MortarTurret(
    #     Vec2.from_cartesian(1500, 100)
    # )
    # SniperTurret(
    #     Vec2.from_cartesian(2000, 900)
    # )
    # SniperTurret(
    #     Vec2.from_cartesian(1500, 100)
    # )
    # SniperTurret(
    #     Vec2.from_cartesian(2000, 900)
    # )
    # AkTurret(
    #     Vec2.from_cartesian(1800, 300)
    # )

    game.mainloop()


if __name__ == "__main__":
    main()

# TODO: bullet interception shitty
