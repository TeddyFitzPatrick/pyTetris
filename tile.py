import pygame

WINDOW_SIZE = (850, 700)  # set the window size

# The size of a tile
TILE_SIZE = 32

# GRID POSITIONING
LEFT_BOUND = TILE_SIZE * 7  # Left Bound
RIGHT_BOUND = LEFT_BOUND + 9 * TILE_SIZE  # Right Bound
LOWER_BOUND = TILE_SIZE * 16  # Lower Bound
UPPER_BOUND = TILE_SIZE * 2  # Upper Bound


class Tile:
    def __init__(self, color: tuple, position: list):
        self.color = color  # color
        self.position = position  # initial position
        # Rect
        self.rect = pygame.rect.Rect(self.position[0], self.position[1], 32, 32)
        # Tile Placed
        self.is_placed = False

    def update(self):
        # Make the rect track the position of the rect surface
        self.rect.x, self.rect.y = self.position[0], self.position[1]

    def move_down(self, placed_tiles, override=False):
        can_move_down = True
        # Check Lower Bound
        if self.position[1] + TILE_SIZE > LOWER_BOUND:
            can_move_down = False
        # Check for collisions with placed tiles
        for placed_tile in placed_tiles:
            # If a placed piece is on the same horizontal and below, the current can't move down.
            if self.position[1] + TILE_SIZE == placed_tile.position[1] and self.position[0] == placed_tile.position[0]:
                can_move_down = False
        if can_move_down or override:
            self.position[1] += TILE_SIZE
            self.update()
        else:
            self.is_placed = True

    def move_left(self):
        if not (self.position[0] - TILE_SIZE < LEFT_BOUND):
            self.position[0] -= TILE_SIZE
            self.update()

    def move_right(self):
        if not (self.position[0] + TILE_SIZE > RIGHT_BOUND):
            self.position[0] += TILE_SIZE
            self.update()
