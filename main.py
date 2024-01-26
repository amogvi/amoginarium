#! venv/bin/python
from amoginarium.controllers import KeyboardController
from amoginarium.base import BaseGame


def main():
    game = BaseGame(debug=True)

    # create controller
    KeyboardController()

    game.mainloop()


if __name__ == "__main__":
    main()
