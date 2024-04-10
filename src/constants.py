# Define the window dimensions
WINDOW_SIZE = (850, 600)

# GRID POSITIONING
TILE_SIZE = 32  # The size of a tile
LEFT_BOUND = TILE_SIZE * 7  # Left Bound
RIGHT_BOUND = LEFT_BOUND + 9 * TILE_SIZE  # Right Bound
LOWER_BOUND = TILE_SIZE * 16  # Lower Bound
UPPER_BOUND = TILE_SIZE * 2  # Upper Bound

# Box dimensions
BORDER_DIMENSIONS = (10 * TILE_SIZE, 15 * TILE_SIZE)
UPCOMING_DIMENSIONS = (5 * TILE_SIZE, 12 * TILE_SIZE)
HELD_DIMENSIONS = (5 * TILE_SIZE, 4 * TILE_SIZE)

# Score increments
POINTS_PER_LINE = 100
POINTS_PER_TETRIS = 800

# Default position of the next tetromino
DEFAULT_POSITIONS = [
    [(5, 2), (6, 2), (7, 2), (8, 2)],
    [(5, 3), (6, 3), (7, 3), (8, 3)],
    [(5, 4), (6, 4), (7, 4), (8, 4)],
    [(5, 5), (6, 5), (7, 5), (8, 5)]
]
# Tetromino types and their corresponding binary position matrices
tetrominos = {
    'I': [[0, 0, 0, 0],
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]],

    'J': [[1, 0, 0],
          [1, 1, 1],
          [0, 0, 0]],

    'L': [[0, 0, 1],
          [1, 1, 1],
          [0, 0, 0]],

    'O': [[1, 1],
          [1, 1]],

    'S': [[0, 1, 1],
          [1, 1, 0],
          [0, 0, 0]],

    'Z': [[1, 1, 0],
          [0, 1, 1],
          [0, 0, 0]],

    'T': [[0, 1, 0],
          [1, 1, 1],
          [0, 0, 0]]
}
# Dict of block type mapped onto block color
tetromino_colors = {
    'I': (0, 255, 255),
    'J': (0, 0, 255),
    'L': (255, 127, 0),
    'O': (255, 255, 0),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'T': (128, 0, 128)
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
