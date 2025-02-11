import pygame
import random
from matrix_rain import MatrixRain  # Import the Matrix effect

def run_game():
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Matrix Jump Game")

    # Colors
    BLACK = (0, 0, 0)

    # Load images
    player_image = pygame.Surface((30, 30))
    player_image.fill((255, 0, 0))  # Red square
    platform_image = pygame.Surface((80, 10))
    platform_image.fill((255, 255, 255))  # White platform

    # Matrix background effect
    matrix_rain = MatrixRain(WIDTH, HEIGHT)

    # Define Player Class
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = player_image
            self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.vel_x = 5
            self.vel_y = 0
            self.gravity = 0.5
            self.jump_strength = 12
            self.on_ground = False

        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.vel_x
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.vel_x
            if keys[pygame.K_SPACE] and self.on_ground:
                self.vel_y = -self.jump_strength
                self.on_ground = False

            self.vel_y += self.gravity
            self.rect.y += self.vel_y

            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.vel_y = 0
                self.on_ground = True

    # Define Platform Class
    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, speed_x, speed_y):
            super().__init__()
            self.image = platform_image
            self.rect = self.image.get_rect(topleft=(x, y))
            self.speed_x = speed_x
            self.speed_y = speed_y

        def update(self):
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.speed_x *= -1
            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.speed_y *= -1

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create player
    player = Player()
    all_sprites.add(player)

    # Create platforms
    for _ in range(5):
        x = random.randint(0, WIDTH - 80)
        y = random.randint(HEIGHT // 2, HEIGHT - 50)
        speed_x = random.choice([-2, 2])
        speed_y = random.choice([-2, 2])
        platform = Platform(x, y, speed_x, speed_y)
        all_sprites.add(platform)
        platforms.add(platform)

    # Game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw Matrix effect first (background)
        matrix_rain.draw(screen)

        # Update sprites
        all_sprites.update()

        # Collision detection
        player.on_ground = False
        if pygame.sprite.spritecollide(player, platforms, False):
            player.vel_y = 0
            player.on_ground = True
            player.rect.y -= 1

        # Draw sprites
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    run_game()
