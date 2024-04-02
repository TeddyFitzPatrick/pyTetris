import random

import pygame
import sys
import copy

from pygame.locals import *

from tetromino import matrix_to_tiles
from tetromino import Tetromino
from widgets.button import Button

clock = pygame.time.Clock()  # setup clock
pygame.init()
pygame.display.set_caption('Tetris')  # set the window title

WINDOW_SIZE = (850, 600)  # set the window size
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen

# How fast the blocks fall (milliseconds)
TICK_SPEED = 1000

# Keep track of the score
score = 0

# The size of a tile
TILE_SIZE = 32

# GRID POSITIONING
LEFT_BOUND = TILE_SIZE * 7  # Left Bound
RIGHT_BOUND = LEFT_BOUND + 9 * TILE_SIZE  # Right Bound
LOWER_BOUND = TILE_SIZE * 16  # Lower Bound
UPPER_BOUND = TILE_SIZE * 2  # Upper Bound

tetrominos = {
    'I': [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    'J': [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    'L': [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    'Z': [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
    'T': [[0, 1, 0], [1, 1, 1], [0, 0, 0]]
}


def get_next_tetromino(randomize=False):
    # Choose a random tetromino type (e.g. 'L', 'T', 'Z', ...)
    tetromino_type = random.choice(list(tetrominos.keys()))
    # Get the corresponding shape
    binary_matrix = tetrominos[tetromino_type]
    # Generate random positions for load screen
    if randomize:
        next_tetromino = Tetromino(tetromino_type, binary_matrix)
        x = random.randint(-11, 11) * 32
        for tile in next_tetromino.tile_group:
            tile.position[0] += x
            tile.position[1] -= 4 * 32
            tile.update()
        return next_tetromino
    # Create the next random tetromino
    return Tetromino(tetromino_type, binary_matrix)


def draw_grid():
    # Generate grid lines
    # 10 horizontal grid boxes
    for x in range(0, TILE_SIZE * 10, TILE_SIZE):
        # 15 vertical grid boxes
        for y in range(0, TILE_SIZE * 15, TILE_SIZE):
            grid_box = pygame.Rect(x + LEFT_BOUND, y + UPPER_BOUND, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (0, 0, 0), grid_box, 1)
    # Create a border around the grid
    border = pygame.Rect(LEFT_BOUND - 5, UPPER_BOUND - 5, TILE_SIZE * 10 + 10, TILE_SIZE * 15 + 10)
    # Draw the border
    pygame.draw.rect(screen, (0, 0, 0), border, 5)


def render_held_tetromino(held_tetromino):
    # Render HELD text
    font = pygame.font.SysFont('', 32)
    held_text = font.render('HELD', True, (5, 5, 5))
    screen.blit(held_text, [TILE_SIZE * 2, TILE_SIZE])
    # Show the held tetromino
    held_surface = pygame.surface.Surface((5 * TILE_SIZE, 4 * TILE_SIZE), 0, 32)
    held_surface.set_colorkey((0, 128, 0))
    held_position = (TILE_SIZE, UPPER_BOUND)
    screen.blit(held_surface, held_position)
    if held_tetromino is not None:
        held_tetromino.tile_group = matrix_to_tiles(held_tetromino.binary_matrix, held_tetromino.color)
        for tile in held_tetromino.tile_group:
            tile.rect.x -= TILE_SIZE * 9
            tile.rect.y += TILE_SIZE
        held_tetromino.draw(screen)


def render_upcoming_tetrominos(upcoming_tetrominos):
    # Create a background for the upcoming tetromino surface

    upcoming_position = (LEFT_BOUND * 2 + TILE_SIZE * 4, UPPER_BOUND)
    upcoming_surface = pygame.surface.Surface((5 * TILE_SIZE, 12 * TILE_SIZE), 0, 32)
    # Render the upcoming surface
    screen.blit(upcoming_surface, upcoming_position)
    # Place all the upcoming tetrominos on this surface
    elevation = -1
    for tetromino in upcoming_tetrominos:
        tetromino.tile_group = matrix_to_tiles(tetromino.binary_matrix, tetromino.color)
        for tile in tetromino.tile_group:
            tile.rect.x += 8 * TILE_SIZE
            tile.rect.y += (2 + elevation) * TILE_SIZE
            pygame.draw.rect(screen, tile.color, tile.rect)
        elevation += 4


def render_stats(tetrominos_placed, time_elapsed):
    # Show a timer in seconds
    font = pygame.font.SysFont('', 24)
    timer = font.render(str(round(time_elapsed / 1000, 2)) + ' seconds', True, (5, 5, 5))
    screen.blit(timer, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 7 + 15])
    # Show the placed piece count
    piece_count = font.render(str(tetrominos_placed) + ' pieces placed', True, (5, 5, 5))
    screen.blit(piece_count, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 8 - 20])
    # Show the placed piece count
    score_count = font.render('score: ' + str(score), True, (5, 5, 5))
    screen.blit(score_count, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 8 + 10])


def remove_lines(placed_tiles):
    global score
    lines_removed = []
    # Make a list of all the rows where placed blocks are.
    rows_to_check = []
    for placed_tile in placed_tiles:
        if not rows_to_check.__contains__(placed_tile.position[1]):
            rows_to_check.append(placed_tile.position[1])
    # Check how many tiles are on a given row
    for check_row in rows_to_check:
        row_coordinates = []
        for placed_tile in placed_tiles:
            if placed_tile.position[1] == check_row and not row_coordinates.__contains__(placed_tile.position[0]):
                row_coordinates.append(placed_tile.position[0])
        # If a row contains blocks on all 10 columns, add the tiles to the remove queue.
        if len(row_coordinates) >= 10:
            lines_removed.append(check_row)
            tiles_to_remove = []
            for placed_tile in placed_tiles:
                if check_row == placed_tile.position[1]:
                    tiles_to_remove.append(placed_tile)
            for tile in tiles_to_remove:
                placed_tiles.remove(tile)
    # Move lines down
    if len(lines_removed) > 0:
        # Increment the score (tetris is bonus points)
        if len(lines_removed) == 4:
            score += 800
        else:
            score += 100 * len(lines_removed)
        # Confusion
        lower_bound = (19 - min(lines_removed)) * TILE_SIZE
        tiles_to_shift = []
        # Add each placed tile to be moved down to a queue
        for placed_tile in placed_tiles:
            if placed_tile.position[1] > lower_bound:
                tiles_to_shift.append(placed_tile)
        # Sort the tile fall order by y position so lower down tiles fall first.
        tiles_to_shift.sort(key=lambda tile_to_shift: tile_to_shift.position[1], reverse=True)
        # Shift the placed tiles down the number of lines removed
        for tile in tiles_to_shift:
            tile.is_placed = False
            for _ in range(len(lines_removed)):
                tile.move_down(placed_tiles)


def main():
    global TICK_SPEED
    # Placed tetrominos and current tetromino
    placed_tiles = []
    tetrominos_placed = 0
    # Add upcoming tetrominos to a queue and generate a current
    current_tetromino = get_next_tetromino()
    held_tetromino = None
    using_held_piece = False
    upcoming_tetrominos = [get_next_tetromino() for _ in range(3)]
    # Tick tracking
    prior_elapsed = 0
    time_elapsed = 1
    place_block_timer = 0

    # game loop
    running = True
    while running:
        # RESET SCREEN
        screen.fill((255, 255, 255))
        # Held tetromino box
        render_held_tetromino(copy.deepcopy(held_tetromino))
        # Upcoming tetrominos
        render_upcoming_tetrominos(upcoming_tetrominos)
        # Stats
        render_stats(tetrominos_placed, time_elapsed)

        # Place a piece when the timer runs out
        if current_tetromino.can_move_down(placed_tiles):
            # Shutdown the timer when piece can move down
            place_block_timer = 0
        elif place_block_timer == 0:
            # Start the timer
            place_block_timer += clock.get_time()
        elif place_block_timer < TICK_SPEED:
            place_block_timer += clock.get_time()
        else:
            current_tetromino.place_tetromino()
            place_block_timer = 0

        # Generate next piece when current is placed
        if current_tetromino.is_placed:
            tetrominos_placed += 1
            using_held_piece = False
            # Add the placed tetromino to the list
            for placed_tile in current_tetromino.tile_group:
                placed_tiles.append(placed_tile)
            # Take a tetromino off the queue
            current_tetromino = upcoming_tetrominos.pop(0)
            # Put a new tetromino on the back of the queue
            upcoming_tetrominos.append(get_next_tetromino())

        # Adjust the tick speed by the score. SPEED UP
        TICK_SPEED = 1000 - (score / 5)
        if TICK_SPEED < 200:
            TICK_SPEED = 200

        # Game ticks -> Tetromino moves down
        time_elapsed += clock.get_time()
        if time_elapsed > prior_elapsed + TICK_SPEED:
            # Every game tick, move the tetromino down and update the tick
            current_tetromino.move_down(placed_tiles)
            prior_elapsed = time_elapsed
        # HANDLE KEY PRESSES
        for event in pygame.event.get():
            # quit type
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Keydown
            if event.type == KEYDOWN:
                # PLACE PIECE BELOW WITH ( SPACE )
                if event.key == pygame.K_SPACE:
                    while not current_tetromino.is_placed:
                        # Move piece down if it can move down, otherwise place it
                        if current_tetromino.can_move_down(placed_tiles):
                            current_tetromino.move_down(placed_tiles)
                        else:
                            current_tetromino.place_tetromino()

                # TURN PIECE WITH ( UP_ARROW OR Z )
                if (event.key == K_UP or event.key == ord('z')) and current_tetromino.type != 'O':
                    current_tetromino.rotate(placed_tiles)
                # HOLD PIECE WITH ( C )
                if event.key == ord('c'):
                    if using_held_piece:
                        break
                    # Hold a piece and refill the queue
                    elif held_tetromino is None:
                        using_held_piece = True
                        held_tetromino = current_tetromino
                        # Take a tetromino off the queue
                        current_tetromino = upcoming_tetrominos.pop(0)
                        # Put a new tetromino on the back of the queue
                        upcoming_tetrominos.append(get_next_tetromino())
                    elif held_tetromino is not None:
                        # Use the held piece
                        using_held_piece = True
                        current_tetromino = held_tetromino
                        # Reset the position
                        current_tetromino.tile_group = matrix_to_tiles(held_tetromino.binary_matrix,
                                                                       held_tetromino.color)
                        # Make the held tetromino slot empty again
                        held_tetromino = None
                # DIRECTIONAL MOVEMENT
                if event.key == K_DOWN:
                    current_tetromino.move_down(placed_tiles)
                if event.key == K_RIGHT:
                    current_tetromino.move_right(placed_tiles)
                if event.key == K_LEFT:
                    current_tetromino.move_left(placed_tiles)

        # Update tetrominos tiles to match their corresponding rects
        current_tetromino.update()
        # Remove full lines of tiles
        remove_lines(placed_tiles)
        # Draw the placed tiles
        for placed_tile in placed_tiles:
            placed_tile.update()
            # Check if the game is over
            if placed_tile.position[1] < UPPER_BOUND * 2:
                load_screen()
                running = False
            pygame.draw.rect(screen, placed_tile.color, placed_tile.rect)
        # Draw the current falling tetromino
        current_tetromino.draw(screen)
        # Draw the  grid
        draw_grid()
        # Display the game
        pygame.display.update()
        # Pause the game to run at 60 FPS
        clock.tick(60)


def load_screen():
    global score
    score = 0
    buttons = [
        Button('Welcome to PyTetris!', x=180, y=70, font_size=50),
        Button('START', 100, 250),
        Button('OPTIONS', 100, 350),
        Button('ABOUT', 100, 450)
    ]
    about = 0
    tetromino = get_next_tetromino(randomize=True)
    # LOOP
    running = True
    while running:
        screen.fill((0, 0, 0))
        tetromino.update()
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                # DIRECTIONAL MOVEMENT
                if event.key == K_DOWN:
                    tetromino.move_down()
                if event.key == K_RIGHT:
                    tetromino.move_right()
                if event.key == K_LEFT:
                    tetromino.move_left()

            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            # START
            if buttons[1].is_pressed():
                main()
                running = False
            # OPTIONS
            if buttons[2].is_pressed():
                buttons[2].update_text("There are none.")
            # ABOUT CLICK
            if buttons[3].is_pressed():
                about += 1
            if about >= 4:
                buttons[3].update_text("Stop it")
            if about >= 7:
                buttons[3].update_text("> - <")
            if about >= 10:
                pygame.quit()
                sys.exit(0)
        # Display all the buttons
        if tetromino.tile_group[0].position[1] > WINDOW_SIZE[1]:
            tetromino = get_next_tetromino(randomize=True)
        # Move the tetromino down and draw it
        tetromino.move_down(override=True)
        tetromino.draw(screen)

        for button in buttons:
            button.blit(screen)
        # Update display
        pygame.display.flip()
        # 60 FPS
        clock.tick(10)


if __name__ == '__main__':
    load_screen()
