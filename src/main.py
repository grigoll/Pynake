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

SPRITE_TILE_SIZE = 64
APPLE_SPRITE = (0 * SPRITE_TILE_SIZE, 3 * SPRITE_TILE_SIZE)  # col=0, row=3
SNAKE_HEAD = {
    UP: (3 * SPRITE_TILE_SIZE, 0 * SPRITE_TILE_SIZE),
    RIGHT: (4 * SPRITE_TILE_SIZE, 0 * SPRITE_TILE_SIZE),
    DOWN: (4 * SPRITE_TILE_SIZE, 1 * SPRITE_TILE_SIZE),
    LEFT: (3 * SPRITE_TILE_SIZE, 1 * SPRITE_TILE_SIZE),
}
SNAKE_TAIL = {
    UP: (3 * SPRITE_TILE_SIZE, 2 * SPRITE_TILE_SIZE),
    RIGHT: (4 * SPRITE_TILE_SIZE, 2 * SPRITE_TILE_SIZE),
    DOWN: (4 * SPRITE_TILE_SIZE, 3 * SPRITE_TILE_SIZE),
    LEFT: (3 * SPRITE_TILE_SIZE, 3 * SPRITE_TILE_SIZE),
}
HORIZ_STRAIGHT = (1 * SPRITE_TILE_SIZE, 0 * SPRITE_TILE_SIZE)
VERT_STRAIGHT = (2 * SPRITE_TILE_SIZE, 1 * SPRITE_TILE_SIZE)
DOWN_RIGHT = (0 * SPRITE_TILE_SIZE, 0 * SPRITE_TILE_SIZE)
UP_RIGHT = (0 * SPRITE_TILE_SIZE, 1 * SPRITE_TILE_SIZE)
DOWN_LEFT = (2 * SPRITE_TILE_SIZE, 0 * SPRITE_TILE_SIZE)
UP_LEFT = (2 * SPRITE_TILE_SIZE, 2 * SPRITE_TILE_SIZE)


class Apple():
    def __init__(self, window_dimensions, tile_size, snake_placement):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        x,  y = self.new_position(snake_placement)
        sprite_x, sprite_y = APPLE_SPRITE

        self.sprite = arcade.Sprite(
            'assets/sprites/snake-graphics.png',
            scale=tile_size / SPRITE_TILE_SIZE,
            image_x=sprite_x,
            image_y=sprite_y,
            image_width=SPRITE_TILE_SIZE,
            image_height=SPRITE_TILE_SIZE,
            center_x=x,
            center_y=y
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

            for s_x, s_y in snake_placement:
                if s_x == x and s_y == y:
                    break
            else:
                return x, y

    def respawn(self, snake_placement):
        x, y = self.new_position(snake_placement)

        self.sprite.center_x = x
        self.sprite.center_y = y

    @property
    def position(self):
        # subtract offset since we only need it when displaying
        return self.sprite.center_x, self.sprite.center_y


class Snake():
    def __init__(self, window_dimensions, tile_size):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        self.size = tile_size
        self.speed = tile_size

        self._direction = RIGHT
        self.direction_locked = False

        self.init_body()

    def init_body(self):
        width, height = self.window_dimensions

        # list of tuples (x, y)
        self.body = list()

        x, y = ((width / 2) - (self.tile_size / 2),
                (height / 2) - (self.tile_size / 2))

        for i in range(3):
            self.body.append((x, y))
            x += self.tile_size

        self.sync_sprites()

    def sync_sprites(self):
        self.sprites = arcade.SpriteList()
        for i, (x, y) in enumerate(self.body):
            if i == len(self.body) - 1:
                img_x, img_y = SNAKE_HEAD[self.direction]

            elif i == 0:
                next_x, next_y = self.body[1]

                if y < next_y:
                    direction = UP
                elif x < next_x:
                    direction = RIGHT
                elif y > next_y:
                    direction = DOWN
                elif x > next_x:
                    direction = LEFT

                img_x, img_y = SNAKE_TAIL[direction]

            else:
                prev_x, prev_y = self.body[i-1]
                next_x, next_y = self.body[i+1]

                if prev_y == y and y == next_y:
                    direction = HORIZ_STRAIGHT
                elif prev_x == x and x == next_x:
                    direction = VERT_STRAIGHT
                elif (x < next_x and y > prev_y) or (y > next_y and x < prev_x):
                    direction = DOWN_RIGHT
                elif (x > next_x and y > prev_y) or (y > next_y and x > prev_x):
                    direction = DOWN_LEFT
                elif (y < next_y and x < prev_x) or (x < next_x and y < prev_y):
                    direction = UP_RIGHT
                elif (y < next_y and x > prev_x) or (x > next_x and y < prev_y):
                    direction = UP_LEFT

                img_x, img_y = direction

            self.sprites.append(arcade.Sprite(
                'assets/sprites/snake-graphics.png',
                scale=self.tile_size / SPRITE_TILE_SIZE,
                image_x=img_x,
                image_y=img_y,
                image_width=SPRITE_TILE_SIZE,
                image_height=SPRITE_TILE_SIZE,
                center_x=x,
                center_y=y,
            ))

    def draw(self):
        self.sprites.draw()

    def move(self, apple_position):
        x, y = self.next_move()
        apple_x, apple_y = apple_position
        did_eat = True

        # snake movement illusion
        self.body.append((x, y))  # add new one at head

        if (apple_x != x or apple_y != y):
            self.body.pop(0)  # remove one from tail
            did_eat = False

        self.direction_locked = False
        self.sync_sprites()

        return did_eat

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

    def reset(self):
        self._direction = RIGHT
        self.direction_locked = False
        self.init_body()

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
        self.set_update_rate(1 / 1)

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

        did_eat = self.snake.move(self.apple.position)

        if did_eat:
            self.apple.respawn(self.snake.placement)

    def on_key_press(self, key, key_modifiers):
        if self.game_over:
            if key == SPACE:
                self.restart()
            return

        # when first starting, game is paused
        if not self.game_started and key in [UP, DOWN, LEFT, RIGHT]:
            self.game_started = True

        if (
            key == UP or
            key == DOWN or
            key == LEFT or
            key == RIGHT
        ):
            self.snake.direction = key

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

        # x, y = self.apple.position
        # sprite = arcade.Sprite(
        #     ':resources:images/tiles/grass_sprout.png',
        #     self.tile_size / 128,
        #     center_x=x + self.tile_size,
        #     center_y=y + self.tile_size,
        # )

        # sprite.draw()

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
