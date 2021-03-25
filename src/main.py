import arcade
from random import randrange
from constants import *

# width & height should be multiple of SQUARE_SIZE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SQUARE_SIZE = 50

UP = arcade.key.UP
RIGHT = arcade.key.RIGHT
DOWN = arcade.key.DOWN
LEFT = arcade.key.LEFT
SPACE = arcade.key.SPACE

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


class Apple():
    def __init__(self, size):
        self.size = size
        self.respawn()

    def draw(self):
        arcade.draw_circle_filled(
            self.x, self.y, self.size / 2, arcade.color.RED
        )

    def respawn(self, snake_placement=None):
        while True:
            X = randrange(
                SQUARE_SIZE / 2, SCREEN_WIDTH - (SQUARE_SIZE / 2), SQUARE_SIZE
            )
            Y = randrange(
                SQUARE_SIZE / 2, SCREEN_HEIGHT - (SQUARE_SIZE / 2), SQUARE_SIZE
            )

            overlaps = False

            if (snake_placement):
                for x, y in snake_placement:
                    overlaps = x == X and y == Y

            if overlaps:
                continue
            else:
                break

        self.x = X
        self.y = Y

    def get_position(self):
        return self.x, self.y


class Snake():
    def __init__(self, size):
        self.size = size
        self.speed = size

        self._direction = None
        self.direction_locked = False

        # list of tuples (x, y)
        self.body = [
            ((SCREEN_WIDTH / 2) - (SQUARE_SIZE / 2),
             (SCREEN_HEIGHT / 2) - (SQUARE_SIZE / 2))
        ]

    def reset(self):
        self._direction = None
        self.direction_locked = False

        # list of tuples (x, y)
        self.body = [
            ((SCREEN_WIDTH / 2) - (SQUARE_SIZE / 2),
             (SCREEN_HEIGHT / 2) - (SQUARE_SIZE / 2))
        ]

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, val):
        if (val not in [UP, DOWN, LEFT, RIGHT]):
            raise ValueError(
                f'Invalid snake direction was provided. Key code:{val}'
            )

        if not self.direction_locked and self.opposite_direction != val:
            self._direction = val
            self.direction_locked = True

    @property
    def opposite_direction(self):
        if self._direction == UP:
            return DOWN
        elif self._direction == DOWN:
            return UP
        elif self._direction == LEFT:
            return RIGHT
        elif self._direction == RIGHT:
            return LEFT
        else:
            return None

    @property
    def placement(self):
        return self.body[:]

    def draw(self):
        for x, y in self.body:
            arcade.draw_point(
                x, y, arcade.color.BLACK, self.size
            )

    def move(self):
        x, y = self.body[-1]  # head position

        if self._direction == UP:
            y += self.speed
        elif self._direction == DOWN:
            y -= self.speed
        elif self._direction == LEFT:
            x -= self.speed
        else:
            x += self.speed

        # snake movement illusion
        self.body.append((x, y))  # add new one at head
        self.body.pop(0)  # remove one from tail

        self.direction_locked = False

    def did_eat(self, apple):
        X, Y = self.body[-1]  # head position
        x, y = apple.get_position()

        if X == x and Y == y:
            self.body.append((x, y))
            return True

        return False

    def next_position(self):
        x, y = self.body[-1]  # head position

        if self._direction == UP:
            y += self.speed
        elif self._direction == DOWN:
            y -= self.speed
        elif self._direction == LEFT:
            x -= self.speed
        else:
            x += self.speed

        return x, y

    def collides_self(self):
        X, Y = self.next_position()

        for x, y in self.body:
            if x == X and y == Y:
                return True

        return False


class Pynake(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, 'Snake')

        self.game_started = False
        self.game_over = False

        self.snake = Snake(SQUARE_SIZE)
        self.apple = Apple(SQUARE_SIZE)

        # goes clockwise (top, right, bottom, left)
        self.borders = (
            int(SCREEN_HEIGHT - SQUARE_SIZE / 2),
            int(SCREEN_WIDTH - SQUARE_SIZE / 2),
            int(0 + SQUARE_SIZE / 2),
            int(0 + SQUARE_SIZE / 2),
        )

        # If you have sprite lists, you should create them here,
        # and set them to None

    def setup(self):
        # Create your sprites and sprite lists here
        self.set_update_rate(1 / 5)

        return self

    def run(self):
        arcade.run()

    def on_draw(self):
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        self.draw_background()
        self.apple.draw()
        self.snake.draw()

        if self.game_over:
            self.draw_game_over()

        # Call draw() on all your sprite lists below

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if not self.game_started or self.game_over:
            return

        if self.hits_border() or self.snake.collides_self():
            self.game_over = True
            return

        self.snake.move()

        if self.snake.did_eat(self.apple):
            self.apple.respawn(self.snake.placement)

    def on_key_press(self, key, key_modifiers):
        # when first starting, game is paused
        if (not self.game_started and key in [UP, DOWN, LEFT, RIGHT]):
            self.game_started = True

        if (
            key == UP or
            key == DOWN or
            key == LEFT or
            key == RIGHT
        ):
            self.snake.direction = key

        if self.game_over and key == SPACE:
            self.restart()

    def hits_border(self):
        x, y = self.snake.next_position()
        top, right, bottom, left = self.borders

        if x < left or x > right or y < bottom or y > top:
            return True

        return False

    def restart(self):
        self.game_over = False
        self.game_started = False
        self.snake.reset()
        self.apple.respawn()

    def draw_background(self):
        color = arcade.color.ANDROID_GREEN

        for y in range(int(SQUARE_SIZE / 2), int(SCREEN_HEIGHT - SQUARE_SIZE / 2) + 1, SQUARE_SIZE):
            for x in range(int(SQUARE_SIZE / 2), int(SCREEN_WIDTH - SQUARE_SIZE / 2) + 1, SQUARE_SIZE):
                arcade.draw_point(x, y, color, SQUARE_SIZE)
                color = (arcade.color.ANDROID_GREEN if color != arcade.color.ANDROID_GREEN
                         else arcade.color.APPLE_GREEN)

            color = (arcade.color.ANDROID_GREEN if color != arcade.color.ANDROID_GREEN
                     else arcade.color.APPLE_GREEN)

    def draw_game_over(self):
        arcade.draw_text(
            "GAME OVER",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            arcade.color.RED,
            40,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )


def main():
    game = Pynake(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup().run()


if __name__ == "__main__":
    main()
