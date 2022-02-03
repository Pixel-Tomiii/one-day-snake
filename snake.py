import pygame
import enum
import time
import random
import os

BG_COLOR = (0, 0, 0)
WORLD_COLOR = (30, 30, 30)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (255, 0, 0)
FOOD_COLOR = (255, 255, 255)
PARTS_AFTER_FOOD = 3
INITIAL_LENGTH = 4
FPS = 16
SCALE = 16


class Direction(enum.IntEnum):
    """Direction class to determine which direction the snake is
    travelling in. Also provides methods for determining if two
    directions are opposites and to get the direction vector."""
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    def reversed(direction1, direction2):
        """Return whether the directions are opposite to each other."""
        return min(direction1, direction2) + 2 == max(direction1, direction2)

    def vector(direction):
        """Returns a vector based on the direction. If the direction does
        not exist, the method returns None."""
        if direction == Direction.UP:
            return (0, -1)
        elif direction == Direction.RIGHT:
            return (1, 0)
        elif direction == Direction.DOWN:
            return (0, 1)
        elif direction == Direction.LEFT:
            return (-1, 0)
        else:
            return None


def scale_world(world):
    """Scales the given world and returns the new scaled surface."""
    return pygame.transform.scale(world, (world.get_width() * SCALE, world.get_height() * SCALE))


def get_next_food_time(food_range):
    """Returns a number between the lowest value of food range and the
    highest value of food range + 1"""
    return random.choice(food_range) + random.random()


def add_vectors(vec1, vec2):
    """Adds two vectors together"""
    return (vec1[0] + vec2[0], vec1[1] + vec2[1])


# Window initialisation.
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width = screen.get_width()
height = screen.get_height()

# Generate the surface which the snake will be rendered on.
world_width = width // SCALE
world_height = height // SCALE
world = pygame.Surface((world_width, world_height))

# Snake information.
# TODO: Change array to circular array with size that can change or size
#       that is constant with the number of squares in the world.
snake = [((world_width // 2), (world_height//2) + y) for y in range(INITIAL_LENGTH)]
spare_parts = 0
direction = []
last_direction = Direction.UP

food = set()
next_food = time.time()
next_food_range = range(1, 5)

# Render information.
next_frame = time.time()
interval = 1 / FPS
running = True
paused = False


# Game loop.
while running:
    # Update events.
    for event in pygame.event.get():
        # Quit event.
        if event.type == pygame.QUIT:
            running = False
            paused = True
            break

        # Key down events.
        if event.type == pygame.KEYDOWN:
            # Quit the game.
            if event.key == pygame.K_ESCAPE:
                running = False
                paused = True
                break
            # Pause game.
            elif event.key == pygame.K_SPACE:
                paused = not paused
                next_food = time.time() + get_next_food_time(next_food_range)
                next_frame = time.time()
            # Movement,
            elif event.key == pygame.K_w:
                direction.append(Direction.UP)
            elif event.key == pygame.K_a:
                direction.append(Direction.LEFT)
            elif event.key == pygame.K_s:
                direction.append(Direction.DOWN)
            elif event.key == pygame.K_d:
                direction.append(Direction.RIGHT)

        # Key released event.
        elif event.type == pygame.KEYUP:
            # Movement keys released.
            # Also tracks last key released when no more keys are
            # pressed.
            if event.key == pygame.K_w:
                direction.remove(Direction.UP)
                if len(direction) == 0:
                    last_direction = Direction.UP
            elif event.key == pygame.K_a:
                direction.remove(Direction.LEFT)
                if len(direction) == 0:
                    last_direction = Direction.LEFT
            elif event.key == pygame.K_s:
                direction.remove(Direction.DOWN)
                if len(direction) == 0:
                    last_direction = Direction.DOWN
            elif event.key == pygame.K_d:
                direction.remove(Direction.RIGHT)
                if len(direction) == 0:
                    last_direction = Direction.RIGHT
            
    # Skip rendering if paused.
    if paused:
        continue
    
    # Render
    current = time.time()

    # Spawn food.
    if current >= next_food:
        food.add((random.randint(0, world_width), random.randint(0, world_height)))
        next_food += get_next_food_time(next_food_range)

    # Render frame.
    if current < next_frame:
        continue
    next_frame += interval

    screen.fill(BG_COLOR)
    world.fill(WORLD_COLOR)

    # Update the snake.
    current_direction = Direction.vector(last_direction if len(direction) == 0 else direction[-1])
    last_body = snake[-1]
    
    for index in range(len(snake) - 1, 0, -1):
        snake[index] = snake[index - 1]
        
    snake[0] = add_vectors(snake[0], current_direction)

    # Check if snake head has collided.
    if snake.count(snake[0]) > 1:
        running = False
        continue

    # Loop head around edges of screen.
    snake[0] = (snake[0][0] % world_width, snake[0][1] % world_height)

    # Add new part if there are parts to add.
    if spare_parts > 0:
        snake.append(last_body)
        spare_parts -= 1

    # Add new parts after eating food.
    if snake[0] in food:
        spare_parts += PARTS_AFTER_FOOD
        food.remove(snake[0])

    # Rendering the snake body onto the world.
    for pos in snake:
        world.set_at(pos, SNAKE_COLOR)

    # Render snake head after rendering all body parts to prevent copying snake data.
    world.set_at(snake[0], SNAKE_HEAD_COLOR)

    # Rendering food.
    for pos in food:
        world.set_at(pos, FOOD_COLOR)

    screen.blit(scale_world(world), (0, 0))
    pygame.display.update()

# Rendering final score.
screen.fill(BG_COLOR)
game_over_font = pygame.font.SysFont("Arial", 80)
score_font = pygame.font.SysFont("Arial", 40)
info_font = pygame.font.SysFont("Arial", 20)

game_over = game_over_font.render("Game Over!", False, (255, 255, 255))
score = score_font.render(f"Score: {len(snake)}", False, (255, 255, 255))
info = info_font.render("Press esc to exit", True, (255, 255, 255))

center_width = width // 2
center_height = height // 2

screen.blit(game_over, (center_width - (game_over.get_width() // 2), center_height - game_over.get_height()))
screen.blit(score, (center_width - (score.get_width() // 2), center_height))
screen.blit(info, (center_width - (info.get_width() // 2), height - info.get_height()))

pygame.display.update()

while True:
    for event in pygame.event.get():
        if not (event.type == pygame.KEYDOWN):
            continue
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            os._exit(0)










