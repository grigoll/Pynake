import arcade
from random import randrange
import constants


class Apple():
    def __init__(self, window_dimensions, tile_size, snake_placement):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        x,  y = self.new_position(snake_placement)
        sprite_x, sprite_y = constants.APPLE_SPRITE

        self.sprite = arcade.Sprite(
            'assets/sprites/snake-graphics.png',
            scale=tile_size / constants.SPRITE_TILE_SIZE,
            image_x=sprite_x,
            image_y=sprite_y,
            image_width=constants.SPRITE_TILE_SIZE,
            image_height=constants.SPRITE_TILE_SIZE,
            center_x=x,
            center_y=y
        )

    def draw(self):
        self.sprite.draw()

    def new_position(self, snake_placement):
        width, height = self.window_dimensions

        while True:
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
        return self.sprite.center_x, self.sprite.center_y
