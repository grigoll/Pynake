import arcade
import constants
from game import Pynake


def main():
    game = Pynake(
        constants.SCREEN_WIDTH,
        constants.SCREEN_HEIGHT,
        constants.TILE_SIZE
    )

    game.setup().run()


if __name__ == "__main__":
    main()
