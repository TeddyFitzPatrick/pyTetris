import pygame
import time
from tile import Tile

WINDOW_SIZE = (850, 700)  # set the window size

# The size of a tile
TILE_SIZE = 32

# GRID POSITIONING
LEFT_BOUND = TILE_SIZE * 7  # Left Bound
RIGHT_BOUND = LEFT_BOUND + 9 * TILE_SIZE  # Right Bound
LOWER_BOUND = TILE_SIZE * 16  # Lower Bound
UPPER_BOUND = TILE_SIZE * 2  # Upper Bound

# Default position of the next tetromino
DEFAULT_POSITIONS = [
    [(5, 2), (6, 2), (7, 2), (8, 2)],
    [(5, 3), (6, 3), (7, 3), (8, 3)],
    [(5, 4), (6, 4), (7, 4), (8, 4)],
    [(5, 5), (6, 5), (7, 5), (8, 5)]
]

tetromino_colors = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 127, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'T': (128, 0, 128)
}


def matrix_to_tiles(binary_matrix, color):
    tile_group = []
    for row in range(len(binary_matrix)):
        for col in range(len(binary_matrix)):
            binary = binary_matrix[row][col]
            if binary == 1:
                coordinates = list(DEFAULT_POSITIONS[row][col])
                tile_position = [LEFT_BOUND - TILE_SIZE + coordinates[0] * TILE_SIZE, coordinates[1] * TILE_SIZE]
                tile_group.append(Tile(color, tile_position))
    return tile_group


class Tetromino:

    def __init__(self, tetromino_type: str, binary_matrix: list[list[int]]):
        # Color and Type
        self.type = tetromino_type
        self.color = tetromino_colors[tetromino_type]
        # The current binary matrix representing the tile_group
        self.binary_matrix = binary_matrix
        # The arrangement of the tetrominos tiles
        self.tile_group = matrix_to_tiles(binary_matrix, self.color)
        self.is_placed = False  # Tetromino is placed (retired)
        # Timer spent touching the ground
        self.timer = 0

    def draw(self, screen) -> None:
        for tile in self.tile_group:
            pygame.draw.rect(screen, self.color, tile.rect)

    def update(self) -> None:
        # Update all the tiles in the tetromino
        for tile in self.tile_group:
            tile.update()

    def rotate(self, placed_tiles) -> None:
        # Sort the tiles and extract the middle element (offset) for rotation
        tile_positions = []
        for tile in self.tile_group:
            tile_positions.append(tuple(tile.position))
        tile_positions.sort(key=lambda position: position[0])
        offset_x = tile_positions[int((len(tile_positions) - 1) / 2)][0]
        # Get the middle x, y offset
        potential_offset = []
        for position in tile_positions:
            if offset_x == position[0]:
                potential_offset.append(position)
        potential_offset.sort(key=lambda position: position[1])
        offset = list(potential_offset[int((len(potential_offset)) / 2)])
        # Offset (x, y) is set to the origin for rotation of (0, 0)
        new_positions = []
        for tile in self.tile_group:
            origin_position = [tile.position[0] - offset[0], offset[1] - tile.position[1]]
            origin_x, origin_y = origin_position[0], origin_position[1]
            # (x, y) -> (-y, x) is a 90-degree clockwise rotation
            rotated_position = [origin_y, -1 * origin_x]
            new_positions.append([rotated_position[0] + offset[0], -1 * (rotated_position[1] - offset[1])])
        can_rotate = True
        for new_position in new_positions:
            if new_position[0] < LEFT_BOUND or new_position[0] > RIGHT_BOUND or new_position[1] > LOWER_BOUND:
                can_rotate = False
                break
            for placed_tile in placed_tiles:
                if new_position == placed_tile.position:
                    can_rotate = False
                    break
        if can_rotate:
            for index in range(len(self.tile_group)):
                self.tile_group[index].position = new_positions[index]
                self.tile_group[index].update()

    def place_tetromino(self):
        self.is_placed = True
        for tile in self.tile_group:
            tile.is_placed = True

    def can_move_down(self, placed_tiles=[]) -> bool:
        # Check for collisions with placed tiles
        for tile in self.tile_group:
            for placed_tile in placed_tiles:
                # If a placed tile shares the same x with a y equal to y + TILE_SIZE, it is below the current.
                if tile.position[1] + TILE_SIZE == placed_tile.position[1] and tile.position[0] == placed_tile.position[
                    0]:
                    return False
        # Check lower bound
        for tile in self.tile_group:
            if tile.position[1] + TILE_SIZE > LOWER_BOUND:
                return False
        return True

    def move_down(self, placed_tiles=[], override=False) -> None:
        # Move tetromino down if possible
        if self.can_move_down(placed_tiles) or override:
            for tile in self.tile_group:
                tile.move_down(placed_tiles, override=True)

    def move_left(self, placed_tiles=[]):
        can_move_left = True
        # Check for leftward placed tiles
        for tile in self.tile_group:
            for placed_tile in placed_tiles:
                if tile.position[0] - TILE_SIZE == placed_tile.position[0] and tile.position[1] == placed_tile.position[
                    1]:
                    can_move_left = False
                    break
        # Check left bound
        for tile in self.tile_group:
            if tile.position[0] - TILE_SIZE < LEFT_BOUND:
                can_move_left = False
        # move each tile leftward
        if can_move_left:
            for tile in self.tile_group:
                tile.move_left()

    def move_right(self, placed_tiles=[]):
        can_move_right = True
        # Check for rightward placed tiles
        for tile in self.tile_group:
            for placed_tile in placed_tiles:
                if tile.position[0] + TILE_SIZE == placed_tile.position[0] and tile.position[1] == placed_tile.position[
                    1]:
                    can_move_right = False
        # Check right bound
        for tile in self.tile_group:
            if tile.position[0] + TILE_SIZE > RIGHT_BOUND:
                can_move_right = False
        # move each tile rightward
        if can_move_right:
            for tile in self.tile_group:
                tile.move_right()
