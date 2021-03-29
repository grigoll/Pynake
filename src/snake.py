import arcade
import constants


class Snake():
    def __init__(self, window_dimensions, tile_size):
        self.tile_size = tile_size
        self.window_dimensions = window_dimensions

        self.size = tile_size
        self.speed = tile_size

        self._direction = constants.RIGHT
        self.direction_cache = None
        self.direction_locked = False

        self.eat_sound = arcade.Sound('assets/audio/eat.mp3')

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
                img_x, img_y = constants.SNAKE_HEAD[self.direction]

            elif i == 0:
                next_x, next_y = self.body[1]

                if y < next_y:
                    direction = constants.UP
                elif x < next_x:
                    direction = constants.RIGHT
                elif y > next_y:
                    direction = constants.DOWN
                elif x > next_x:
                    direction = constants.LEFT

                img_x, img_y = constants.SNAKE_TAIL[direction]

            else:
                prev_x, prev_y = self.body[i-1]
                next_x, next_y = self.body[i+1]

                if prev_y == y == next_y:
                    direction = constants.HORIZ_STRAIGHT
                elif prev_x == x == next_x:
                    direction = constants.VERT_STRAIGHT
                elif (x < next_x and y > prev_y) or (y > next_y and x < prev_x):
                    direction = constants.DOWN_RIGHT
                elif (x > next_x and y > prev_y) or (y > next_y and x > prev_x):
                    direction = constants.DOWN_LEFT
                elif (y < next_y and x < prev_x) or (x < next_x and y < prev_y):
                    direction = constants.UP_RIGHT
                elif (y < next_y and x > prev_x) or (x > next_x and y < prev_y):
                    direction = constants.UP_LEFT

                img_x, img_y = direction

            self.sprites.append(arcade.Sprite(
                'assets/sprites/snake-graphics.png',
                scale=self.tile_size / constants.SPRITE_TILE_SIZE,
                image_x=img_x,
                image_y=img_y,
                image_width=constants.SPRITE_TILE_SIZE,
                image_height=constants.SPRITE_TILE_SIZE,
                center_x=x,
                center_y=y,
            ))

    def draw(self):
        self.sprites.draw()

    def move(self, apple_position):
        x, y = self.next_move()
        apple_x, apple_y = apple_position

        did_eat = apple_x == x and apple_y == y

        # snake movement illusion
        self.body.append((x, y))  # add new one at head

        if did_eat:
            self.eat_sound.play()
        else:
            self.body.pop(0)  # remove one from tail

        self.sync_sprites()

        return did_eat

    def update(self, apple_position):
        self.direction_locked = False

        did_eat = self.move(apple_position)

        if self.direction_cache is not None:
            self.direction = self.direction_cache
            self.direction_cache = None

        return did_eat

    def next_move(self):
        x, y = self.body[-1]  # head position

        if self.direction == constants.UP:
            y += self.speed
        elif self.direction == constants.DOWN:
            y -= self.speed
        elif self.direction == constants.LEFT:
            x -= self.speed
        else:
            x += self.speed

        return x, y

    def collides_self(self):
        next_x, next_y = self.next_move()

        for x, y in self.body:
            if x == next_x and y == next_y:
                return True

        return False

    def reset(self):
        self._direction = constants.RIGHT
        self.direction_locked = False
        self.direction_cache = None
        self.init_body()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, val):
        if (val not in [constants.UP, constants.DOWN, constants.LEFT, constants.RIGHT]):
            raise ValueError(
                f'Invalid snake direction was provided. Key code:{val}'
            )

        if not self.direction_locked and self.opposite_direction != val:
            self._direction = val
            self.direction_locked = True
        elif self.direction_locked:
            self.direction_cache = val

    @property
    def opposite_direction(self):
        if self.direction == constants.UP:
            return constants.DOWN
        elif self.direction == constants.DOWN:
            return constants.UP
        elif self.direction == constants.LEFT:
            return constants.RIGHT
        elif self.direction == constants.RIGHT:
            return constants.LEFT
        else:
            return None

    @property
    def placement(self):
        return self.body[:]
