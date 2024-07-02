import copy

from constants import *
from tile import Tile


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


def get_default_origin(tetromino_type: str) -> list[int]:
    # The square piece cannot rotate.
    if tetromino_type == 'O':
        return [0, 0]
    # The aqua-colored straight piece has a special rotation point in between its middle tiles
    if tetromino_type == 'I':
        return [416, 96]
    # Every other tetromino type has the same default origin because they're 3x3
    return [384, 96]


class Tetromino:
    def __init__(self, tetromino_type: str, binary_matrix: list[list[int]]):
        self.origin_cords = get_default_origin(tetromino_type)
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

        # The shadow tetromino showing the player where the piece will drop
        self.shadow = copy.deepcopy(self)
        self.shadow.color = (int(0.5 * self.color[0]),
                             int(0.5 * self.color[1]),
                             int(0.5 * self.color[2]))

    def draw(self, screen) -> None:
        for tile in self.tile_group:
            pygame.draw.rect(screen, self.color, tile.rect)

    def update(self) -> None:
        # Update all the tiles in the tetromino
        for tile in self.tile_group:
            tile.update()

    def rotate(self, placed_tiles=()) -> None:
        # Create a list of new rotated positions for each tile
        rotated_positions = []
        for tile in self.tile_group:
            # Get the tile's (x, y) coordinates relative to the designated origin
            origin_pos = [tile.position[0] - self.origin_cords[0], tile.position[1] - self.origin_cords[1]]
            # Rotate the coordinates by translating (x, y) to (-y, x)
            rotated_positions.append([-origin_pos[1] + self.origin_cords[0], origin_pos[0] + self.origin_cords[1]])
        can_rotate = True

        # Check that the tetromino rotation does not go out of bounds or interfere with other tiles
        for new_position in rotated_positions:
            # Check that each tile is within bounds after rotation
            if new_position[0] < LEFT_BOUND or new_position[0] > RIGHT_BOUND or new_position[1] < UPPER_BOUND or new_position[1] > LOWER_BOUND:
                can_rotate = False
                break
            # Check that each tile in the tetromino won't overlap with an existing tile
            for placed_tile in placed_tiles:
                if new_position == placed_tile.position:
                    can_rotate = False
                    break
        # Set the coordinates of each tile to the new rotated coordinates
        if can_rotate:
            for index in range(len(self.tile_group)):
                self.tile_group[index].position = rotated_positions[index]
                self.tile_group[index].update()

    def place_tetromino(self):
        self.is_placed = True
        for tile in self.tile_group:
            tile.is_placed = True

    def can_move_down(self, placed_tiles=()) -> bool:
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

    def move_down(self, placed_tiles=(), check_bound=True) -> None:
        # Move tetromino down if possible
        if self.can_move_down(placed_tiles) or not check_bound:
            self.origin_cords[1] += TILE_SIZE
            for tile in self.tile_group:
                tile.move_down(placed_tiles, check_bound)
        else:
            self.place_tetromino()

    def move_left(self, placed_tiles=(), check_bound=True):
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
            if check_bound and tile.position[0] - TILE_SIZE < LEFT_BOUND:
                can_move_left = False
        # Move each tile leftward
        if can_move_left:
            self.origin_cords[0] -= TILE_SIZE
            for tile in self.tile_group:
                tile.move_left(check_bound)

    def move_right(self, placed_tiles=(), check_bound=True):
        can_move_right = True
        # Check for rightward placed tiles
        for tile in self.tile_group:
            for placed_tile in placed_tiles:
                if tile.position[0] + TILE_SIZE == placed_tile.position[0] and tile.position[1] == placed_tile.position[
                    1]:
                    can_move_right = False
        # Check right bound
        for tile in self.tile_group:
            if check_bound and tile.position[0] + TILE_SIZE > RIGHT_BOUND:
                can_move_right = False
        # Move each tile rightward
        if can_move_right:
            self.origin_cords[0] += TILE_SIZE
            for tile in self.tile_group:
                tile.move_right(check_bound)
