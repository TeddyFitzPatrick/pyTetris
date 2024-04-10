import pygame
from constants import *


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

    def move_down(self, placed_tiles: list, check_bound=True):
        can_move_down = True
        # Check Lower Bound
        if self.position[1] + TILE_SIZE > LOWER_BOUND:
            can_move_down = False
        # Check for collisions with placed tiles
        for placed_tile in placed_tiles:
            # If a placed piece is on the same horizontal and below, the current can't move down.
            if self.position[1] + TILE_SIZE == placed_tile.position[1] and self.position[0] == placed_tile.position[0]:
                can_move_down = False
        if can_move_down or not check_bound:
            # Move the tile down
            self.position[1] += TILE_SIZE
            self.update()
        else:
            # Don't move the tile, and mark it as placed
            self.is_placed = True

    def move_left(self, check_bound=True):
        if not (self.position[0] - TILE_SIZE < LEFT_BOUND) or not check_bound:
            self.position[0] -= TILE_SIZE
            self.update()

    def move_right(self, check_bound=True):
        if not (self.position[0] + TILE_SIZE > RIGHT_BOUND) or not check_bound:
            self.position[0] += TILE_SIZE
            self.update()
