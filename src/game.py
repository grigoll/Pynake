import arcade
from snake import Snake
from apple import Apple
import constants


class Pynake(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width, height, 'Pynake')
        self.tile_size = tile_size

    def setup(self):
        self.set_update_rate(1 / 8)  # fps

        self.game_started = False
        self.game_over = False
        self.score = 0

        self.snake = Snake(
            (self.width, self.height),
            self.tile_size
        )
        self.apple = Apple(
            (self.width, self.height),
            self.tile_size,
            self.snake.placement
        )

        # goes clockwise (top, right, bottom, left)
        self.borders = (
            int(self.height - self.tile_size / 2),
            int(self.width - self.tile_size / 2),
            int(0 + self.tile_size / 2),
            int(0 + self.tile_size / 2),
        )

        self.death_sound = arcade.Sound('assets/audio/death.mp3')

        return self

    def run(self):
        arcade.run()

    def on_draw(self):
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        self.draw_background()
        self.draw_score()
        self.apple.draw()
        self.snake.draw()

        if self.game_over:
            self.draw_game_over()

        if not self.game_started:
            self.draw_start_guide()

    def on_update(self):
        if not self.game_started or self.game_over:
            return

        if self.hits_border() or self.snake.collides_self():
            self.finalize_game()
            return

        did_eat = self.snake.update(self.apple.position)

        if did_eat:
            self.score += 10
            self.apple.respawn(self.snake.placement)

    def on_key_press(self, key):
        if self.game_over:
            if key == constants.SPACE:
                self.restart()
            return

        # when first starting, game is paused
        if not self.game_started and key in [constants.UP, constants.DOWN, constants.LEFT, constants.RIGHT]:
            self.game_started = True

        if (
            key == constants.UP or
            key == constants.DOWN or
            key == constants.LEFT or
            key == constants.RIGHT
        ):
            self.snake.direction = key

    def hits_border(self):
        x, y = self.snake.next_move()
        top, right, bottom, left = self.borders

        if x < left or x > right or y < bottom or y > top:
            return True

        return False

    def finalize_game(self):
        self.game_over = True
        self.death_sound.play()

    def restart(self):
        self.game_over = False
        self.game_started = False
        self.score = 0
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
            self.height * 2 / 3,
            arcade.color.RED,
            40,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            "Press SPACE to start over",
            self.width / 2,
            self.height * 2 / 3 - self.tile_size * 2,
            arcade.color.BLACK_OLIVE,
            20,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def draw_start_guide(self):
        arcade.draw_text(
            "Press Arrow keys to start",
            self.width / 2,
            self.height * 2 / 3,
            arcade.color.BLACK_OLIVE,
            40,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def draw_score(self):
        arcade.draw_text(
            f'{self.score}',
            self.tile_size / 8,
            self.height - self.tile_size / 2,
            arcade.color.BLACK_OLIVE,
            16,
            anchor_y="center"
        )
