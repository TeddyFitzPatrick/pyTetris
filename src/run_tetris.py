import random

import sys

from pygame.locals import *

from tetromino import *
from button import Button

clock = pygame.time.Clock()  # setup clock
pygame.init()
pygame.display.set_caption('Tetris')  # set the window title
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate screen
# How fast the blocks fall (milliseconds)
TICK_SPEED = 1000
score = 0  # Keep track of the score
high_score = 0


def get_next_tetromino():
    # Choose a random tetromino type (e.g. 'L', 'T', 'Z', ...)
    tetromino_type = random.choice(list(tetrominos.keys()))
    # Get the corresponding shape
    binary_matrix = tetrominos[tetromino_type]
    # Create the next random tetromino
    return Tetromino(tetromino_type, binary_matrix)


def draw_grid(start_position: tuple[int] | list[int], horizontal_size: int, vertical_size: int):
    # Generate grid lines
    # 10 horizontal grid boxes
    for x in range(0, horizontal_size, TILE_SIZE):
        # 15 vertical grid boxes
        for y in range(0, vertical_size, TILE_SIZE):
            grid_box = pygame.Rect(start_position[0] + x, start_position[1] + y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (0, 0, 0), grid_box, GRID_WIDTH)


def render_held_tetromino(held_tetromino):
    # Render HELD text
    held_text = MAIN_FONT.render('HELD', True, (5, 5, 5))
    screen.blit(held_text, [TILE_SIZE * 2, TILE_SIZE])
    # Show the held tetromino
    held_surface = pygame.surface.Surface(HELD_DIMENSIONS, 0, 32)
    held_surface.set_colorkey((0, 128, 0))
    screen.blit(held_surface, HELD_POSITION)
    if held_tetromino is not None:
        held_tetromino.tile_group = matrix_to_tiles(held_tetromino.binary_matrix, held_tetromino.color)
        for tile in held_tetromino.tile_group:
            tile.rect.x -= TILE_SIZE * 9
            tile.rect.y += TILE_SIZE
        held_tetromino.draw(screen)
    # Draw the grid
    draw_grid(HELD_POSITION, HELD_DIMENSIONS[0], HELD_DIMENSIONS[1])


def render_upcoming_tetrominos(upcoming_tetrominos):
    # Create a background for the upcoming tetromino surface
    upcoming_surface = pygame.surface.Surface(UPCOMING_DIMENSIONS, 0, 32)
    # Render the upcoming surface
    screen.blit(upcoming_surface, UPCOMING_BLOCK_POSITION)
    # Place all the upcoming tetrominos on this surface
    elevation = -1
    for tetromino in upcoming_tetrominos:
        tetromino.tile_group = matrix_to_tiles(tetromino.binary_matrix, tetromino.color)
        for tile in tetromino.tile_group:
            tile.rect.x += 8 * TILE_SIZE
            tile.rect.y += (2 + elevation) * TILE_SIZE
            pygame.draw.rect(screen, tile.color, tile.rect)
        elevation += 4
    # Generate grid lines
    draw_grid(UPCOMING_BLOCK_POSITION, UPCOMING_DIMENSIONS[0], UPCOMING_DIMENSIONS[1])
    # 10 horizontal grid boxes
    for x in range(0, TILE_SIZE * 5, TILE_SIZE):
        # 15 vertical grid boxes
        for y in range(0, TILE_SIZE * 12, TILE_SIZE):
            grid_box = pygame.Rect(x + UPCOMING_BLOCK_POSITION[0], y + UPCOMING_BLOCK_POSITION[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (0, 0, 0), grid_box, 1)


def render_stats(tetrominos_placed, time_elapsed):
    # Show a timer in seconds
    timer = MAIN_FONT.render(str(round(time_elapsed / 1000, 2)) + ' seconds', True, (5, 5, 5))
    screen.blit(timer, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 7 + 15])
    # Show the placed piece count
    piece_count = MAIN_FONT.render(str(tetrominos_placed) + ' pieces placed', True, (5, 5, 5))
    screen.blit(piece_count, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 8 - 20])
    # Show the placed piece count
    score_count = MAIN_FONT.render('score: ' + str(score), True, (5, 5, 5))
    screen.blit(score_count, [2 * LEFT_BOUND + 4 * TILE_SIZE, UPPER_BOUND * 8 + 10])


def remove_lines(placed_tiles):
    global score
    lines_removed = []
    # Make a list of all the rows where placed blocks are.
    rows_to_check = []
    for placed_tile in placed_tiles:
        if placed_tile.position[1] not in rows_to_check:
            rows_to_check.append(placed_tile.position[1])
    # Check each row for a full line
    for check_row in rows_to_check:
        row_coordinates = []
        for placed_tile in placed_tiles:
            if placed_tile.position[1] == check_row and placed_tile.position[0] not in row_coordinates:
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
        score += POINTS_PER_TETRIS if len(lines_removed) == 4 else POINTS_PER_LINE * len(lines_removed)
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
        screen.fill(WHITE)
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
        # Adjust the tick speed to the score
        TICK_SPEED = 1000 - ((825/4000) * score)
        if TICK_SPEED < 150:
            TICK_SPEED = 150
        # Game ticks -> Tetromino moves down
        time_elapsed += clock.get_time()
        if time_elapsed > prior_elapsed + TICK_SPEED:
            # Gravity (every game tick, move the tetromino down and update the prior tick checkpoint)
            current_tetromino.move_down(placed_tiles)
            prior_elapsed = time_elapsed
        # HANDLE KEY PRESSES
        for event in pygame.event.get():
            # QUIT
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Key-down
            if event.type == KEYDOWN:
                # PLACE PIECE BELOW WITH ( SPACE )
                if event.key == pygame.K_SPACE:
                    while not current_tetromino.is_placed:
                        # Move piece down if it can move down, otherwise place it
                        current_tetromino.move_down(placed_tiles)
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
                        # Reset the position and origin position
                        current_tetromino.origin_cords = get_default_origin(current_tetromino.type)
                        current_tetromino.tile_group = matrix_to_tiles(held_tetromino.binary_matrix, held_tetromino.color)
                        # Make the held tetromino slot empty again
                        held_tetromino = None
                        # Generate the shadow tetromino
                # DIRECTIONAL MOVEMENT
                if event.key == K_DOWN or event.key == ord('s'):
                    current_tetromino.move_down(placed_tiles)
                if event.key == K_RIGHT or event.key == ord('d'):
                    current_tetromino.move_right(placed_tiles)
                if event.key == K_LEFT or event.key == ord('a'):
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
        # Draw the shadow tetromino underneath the falling tetromino
        # current_tetromino.shadow.draw(screen)

        # Draw the grid
        draw_grid([LEFT_BOUND, UPPER_BOUND], BORDER_DIMENSIONS[0], BORDER_DIMENSIONS[1])
        # Create a border around the grid
        border = pygame.Rect(LEFT_BOUND - 5, UPPER_BOUND - 5, TILE_SIZE * 10 + 10, TILE_SIZE * 15 + 10)
        # Draw the border
        pygame.draw.rect(screen, (0, 0, 0), border, 5)
        # Display the game
        pygame.display.update()
        # Pause the game to run at 60 FPS
        clock.tick(60)


def get_five_random_tetrominos():
    random_tetrominos = [get_next_tetromino() for _ in range(5)]
    count = 0
    for tetromino in random_tetrominos:
        for tile in tetromino.tile_group:
            tile.position[0] -= TILE_SIZE * int(WINDOW_SIZE[0] / (2 * TILE_SIZE)) - 4 * TILE_SIZE
            tile.position[0] += count * TILE_SIZE * 5
            tile.position[1] -= UPPER_BOUND + TILE_SIZE
        count += 1
    return random_tetrominos


def load_screen():
    global score
    # Create the title buttons
    title_card = Button('Welcome to PyTetris!', x=180, y=70, font_size=50)
    start = Button('START', x=100, y=250)
    # options = Button('OPTIONS', x=100, y=350)

    # Get the next tetromino
    random_tetrominos = get_five_random_tetrominos()
    running = True
    while running:
        screen.fill(BLACK)
        for tetromino in random_tetrominos:
            tetromino.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            # START
            if start.is_pressed():
                main()
                running = False
            # OPTIONS
            # if options.is_pressed():
            #     pass
        # Move the tetromino down and draw it
        for tetromino in random_tetrominos:
            tetromino.move_down(check_bound=False)
            tetromino.draw(screen)
            if tetromino.tile_group[0].position[1] > WINDOW_SIZE[1]:
                random_tetrominos = get_five_random_tetrominos()
        # Draw the grid
        draw_grid([0, 0], WINDOW_SIZE[0], WINDOW_SIZE[1])
        # Display all the buttons
        for button in [title_card, start]:
            button.blit(screen)
        # Update display
        pygame.display.flip()
        # 60 FPS
        clock.tick(10)


if __name__ == '__main__':
    load_screen()
    # main()