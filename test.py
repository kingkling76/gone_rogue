import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Jump Game")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Font settings
FONT_SIZE = 20
font = pygame.font.SysFont('Courier', FONT_SIZE, bold=True)

# Player settings
player_size = 30
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 50  # Start above the ground
player_vel = 5
jump_strength = 12
gravity = 0.5
player_dy = 0  # Vertical velocity
on_ground = False

# Platform settings
platform_width = 80
platform_height = 10
platforms = []

# Create initial platforms
for _ in range(5):
    x = random.randint(0, WIDTH - platform_width)
    y = random.randint(HEIGHT // 2, HEIGHT - 50)  # Platforms appear lower
    speed_x = random.choice([-2, 2])
    speed_y = random.choice([-2, 2])
    platforms.append([x, y, speed_x, speed_y])

# Matrix settings
columns = WIDTH // FONT_SIZE
matrix = [{'x': x * FONT_SIZE, 'y': random.randint(-HEIGHT, 0),
           'stream': [random.choice(['0', '1']) for _ in range(random.randint(5, 15))]} for x in range(columns)]

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_vel
    if keys[pygame.K_RIGHT]:
        player_x += player_vel
    if keys[pygame.K_SPACE] and on_ground:
        player_dy = -jump_strength
        on_ground = False

    # Apply gravity
    player_dy += gravity
    player_y += player_dy

    # Prevent player from falling off screen
    if player_y > HEIGHT:
        player_y = HEIGHT - player_size  # Reset to bottom (for now)
        player_dy = 0
        on_ground = True

    # Check for platform collisions
    on_ground = False
    for platform in platforms:
        px, py, _, _ = platform
        if px < player_x + player_size and px + platform_width > player_x:  # X collision
            if py < player_y + player_size <= py + platform_height + player_dy:  # Y collision (falling onto platform)
                player_y = py - player_size
                player_dy = 0
                on_ground = True

    # Move platforms
    for platform in platforms:
        platform[0] += platform[2]  # Move X
        platform[1] += platform[3]  # Move Y

        # Bounce when hitting screen edges
        if platform[0] <= 0 or platform[0] + platform_width >= WIDTH:
            platform[2] *= -1
        if platform[1] <= 0 or platform[1] + platform_height >= HEIGHT:
            platform[3] *= -1

    # Draw Matrix effect
    for col in matrix:
        for i, char in enumerate(col['stream']):
            y_pos = col['y'] + i * FONT_SIZE
            if 0 <= y_pos < HEIGHT:
                color = GREEN if i < len(col['stream']) - 1 else DARK_GREEN
                char_surface = font.render(char, True, color)
                screen.blit(char_surface, (col['x'], y_pos))

        col['y'] += FONT_SIZE // 2
        if col['y'] - len(col['stream']) * FONT_SIZE > HEIGHT:
            col['y'] = random.randint(-100, 0)
            col['stream'] = [random.choice(['0', '1']) for _ in range(random.randint(5, 15))]

    # Draw player
    pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, WHITE, (platform[0], platform[1], platform_width, platform_height))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
