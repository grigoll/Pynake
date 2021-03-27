import arcade
from random import randrange
from constants import *

# width & height should be multiple of TILE_SIZE
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50

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
    def __init__(self, window_dimensions, tile_size, snake_placement):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        self.size = tile_size

        sprite_orig_size = 100
        # this is how much sprite is misaligned on Y axis when shown by original size
        sprite_offset_y = 36
        # magic number to push sprite upwards, otherwise it's a bit off by default
        self.offset_y = sprite_offset_y * tile_size / sprite_orig_size

        x,  y = self.new_position(snake_placement)

        self.sprite = arcade.Sprite(
            ":resources:images/enemies/mouse.png",
            tile_size / sprite_orig_size,
            center_x=x,
            center_y=y + self.offset_y
        )

    def draw(self):
        self.sprite.draw()

    def new_position(self, snake_placement):
        while True:
            width, height = self.window_dimensions

            x = randrange(
                self.tile_size / 2,
                width - (self.tile_size / 2),
                self.tile_size
            )
            y = randrange(
                self.tile_size / 2,
                height - (self.tile_size / 2),
                self.tile_size
            )

            overlaps = False

            for s_x, s_y in snake_placement:
                if s_x == x and s_y == y:
                    overlaps = True
                    break

            if not overlaps:
                return x, y

    def respawn(self, snake_placement):
        x, y = self.new_position(snake_placement)

        self.sprite.center_x = x
        self.sprite.center_y = y + self.offset_y  # keep offset in mind

    @property
    def position(self):
        # subtract offset since we only need it when displaying
        return self.sprite.center_x, self.sprite.center_y - self.offset_y


class Snake():
    def __init__(self, window_dimensions, tile_size):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        self.size = tile_size
        self.speed = tile_size

        self._direction = None
        self.direction_locked = False

        width, height = self.window_dimensions

        # list of tuples (x, y)
        self.body = [
            ((width / 2) - (tile_size / 2),
             (height / 2) - (tile_size / 2))
        ]

    def reset(self):
        self._direction = None
        self.direction_locked = False

        width, height = self.window_dimensions

        # list of tuples (x, y)
        self.body = [
            ((width / 2) - (self.tile_size / 2),
             (height / 2) - (self.tile_size / 2))
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
        if self.direction == UP:
            return DOWN
        elif self.direction == DOWN:
            return UP
        elif self.direction == LEFT:
            return RIGHT
        elif self.direction == RIGHT:
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

        if self.direction == UP:
            y += self.speed
        elif self.direction == DOWN:
            y -= self.speed
        elif self.direction == LEFT:
            x -= self.speed
        else:
            x += self.speed

        # snake movement illusion
        self.body.append((x, y))  # add new one at head
        self.body.pop(0)  # remove one from tail

        self.direction_locked = False

    def did_eat(self, apple_position):
        X, Y = self.body[-1]  # head position
        x, y = apple_position

        if X == x and Y == y:
            self.body.append((x, y))
            return True

        return False

    def next_move(self):
        x, y = self.body[-1]  # head position

        if self.direction == UP:
            y += self.speed
        elif self.direction == DOWN:
            y -= self.speed
        elif self.direction == LEFT:
            x -= self.speed
        else:
            x += self.speed

        return x, y

    def collides_self(self):
        X, Y = self.next_move()

        for x, y in self.body:
            if x == X and y == Y:
                return True

        return False


class Pynake(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width, height, 'Snake')

        self.tile_size = tile_size

        self.game_started = False
        self.game_over = False

        self.snake = Snake((width, height), tile_size)
        self.apple = Apple((width, height), tile_size, self.snake.placement)

        # goes clockwise (top, right, bottom, left)
        self.borders = (
            int(height - tile_size / 2),
            int(width - tile_size / 2),
            int(0 + tile_size / 2),
            int(0 + tile_size / 2),
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

        if self.snake.did_eat(self.apple.position):
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
        x, y = self.snake.next_move()
        top, right, bottom, left = self.borders

        if x < left or x > right or y < bottom or y > top:
            return True

        return False

    def restart(self):
        self.game_over = False
        self.game_started = False
        self.snake.reset()
        self.apple.respawn(self.snake.placement)

    def draw_background(self):
        color = arcade.color.ANDROID_GREEN

        for y in range(int(self.tile_size / 2), int(self.height - self.tile_size / 2) + 1, self.tile_size):
            for x in range(int(self.tile_size / 2), int(self.width - self.tile_size / 2) + 1, self.tile_size):
                arcade.draw_point(x, y, color, self.tile_size)
                color = (arcade.color.ANDROID_GREEN if color != arcade.color.ANDROID_GREEN
                         else arcade.color.APPLE_GREEN)

            color = (arcade.color.ANDROID_GREEN if color != arcade.color.ANDROID_GREEN
                     else arcade.color.APPLE_GREEN)

    def draw_game_over(self):
        arcade.draw_text(
            "GAME OVER",
            self.width / 2,
            self.height / 2,
            arcade.color.RED,
            40,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )


def main():
    game = Pynake(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
    game.setup().run()


if __name__ == "__main__":
    main()
