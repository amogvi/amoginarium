#! venv/bin/python
from amoginarium.base import BaseGame
from amoginarium.controllers import KeyboardController


def main():
    game = BaseGame(debug=True)

    # create controller
    KeyboardController()

    game.mainloop()


if __name__ == "__main__":
    main()
