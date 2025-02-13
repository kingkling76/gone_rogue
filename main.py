import pygame
import random

from matrix_rain import MatrixRain
from enemy import Enemy
from platforms import Platform
from startscreen import StartupScreen


def run_game():
    pygame.init()
    
    # Initialize display
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Matrix Jump Game")
    
    # Show startup screen
    startup = StartupScreen(screen, WIDTH, HEIGHT)
    player_name = startup.show()
    if player_name is None:  # Player closed the window
        return False
    
    # Colors
    BLACK = (0, 0, 0)
    
    # Load images
    player_image = pygame.Surface((30, 30))
    player_image.fill((255, 0, 0))  # Red square
    
    # Matrix background effect
    matrix_rain = MatrixRain(WIDTH, HEIGHT)
    
    # Define Player Class
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = player_image
            self.rect = self.image.get_rect()
            self.vel_x = 5
            self.vel_y = 0
            self.gravity = 0.5
            self.jump_strength = 12
            self.on_platform = False
            
        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.vel_x
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.vel_x
            if keys[pygame.K_SPACE] and self.on_platform:
                self.vel_y = -self.jump_strength
                self.on_platform = False
                
            # Apply gravity
            self.vel_y += self.gravity
            self.rect.y += self.vel_y
            
            # Keep player in bounds horizontally
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                
            # Check if player fell off screen
            if self.rect.top > HEIGHT:
                return True  # Player died
            return False
    
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    
    # Create initial platform and player
    class StartPlatform(Platform):
        def __init__(self, screen_width):
            super().__init__(screen_width)
            self.rect.centerx = screen_width // 2
            self.rect.y = HEIGHT - 100
            self.speed = 0
            self.has_jumped = False  # Track if player has jumped

    initial_platform = StartPlatform(WIDTH)
    all_sprites.add(initial_platform)
    platforms.add(initial_platform)

    # Create player on the initial platform
    player = Player()
    player.rect.bottom = initial_platform.rect.top
    player.rect.centerx = initial_platform.rect.centerx
    all_sprites.add(player)
    
    # Game variables
    enemy_spawn_timer = 0
    platform_spawn_timer = 0
    enemy_spawn_delay = 120  # Frames between enemy spawns
    platform_spawn_delay = 60  # Frames between platform spawns
    score = 0
    game_over = False
    running = True
    clock = pygame.time.Clock()
    
    while running:
        if not game_over:
            # Handle events during gameplay
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            
            screen.fill(BLACK)
            matrix_rain.draw(screen)
            
            # Spawn enemies
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                enemy_spawn_timer = 0
                enemy = Enemy(WIDTH, HEIGHT)
                all_sprites.add(enemy)
                enemies.add(enemy)
                
            # Spawn platforms
            platform_spawn_timer += 1
            if platform_spawn_timer >= platform_spawn_delay:
                platform_spawn_timer = 0
                platform = Platform(WIDTH)
                all_sprites.add(platform)
                platforms.add(platform)
                
            # Update sprites
            all_sprites.update()
            
            # Check if player fell off screen
            if player.update():
                game_over = True
                
            # Platform collision detection
            player.on_platform = False
            for platform in platforms:
                if (player.rect.bottom >= platform.rect.top and 
                    player.rect.bottom <= platform.rect.bottom and 
                    player.rect.right >= platform.rect.left and 
                    player.rect.left <= platform.rect.right and 
                    player.vel_y >= 0):
                    player.rect.bottom = platform.rect.top
                    player.vel_y = 0
                    player.on_platform = True
                    # Move player with platform
                    player.rect.x += platform.speed
                    # Track if it's the initial platform
                    if isinstance(platform, StartPlatform):
                        platform.has_jumped = False

            # Check if player has left the initial platform
            for platform in platforms:
                if isinstance(platform, StartPlatform) and not player.on_platform and not platform.has_jumped:
                    platform.has_jumped = True
                    platform.kill()  # Remove the initial platform
                    
            # Check for collisions with enemies
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True
                
            # Remove sprites that are off screen
            for sprite in platforms:
                if (sprite.direction == -1 and sprite.rect.left > WIDTH) or \
                   (sprite.direction == 1 and sprite.rect.right < 0):
                    sprite.kill()
            for enemy in enemies:
                if (enemy.rect.right < 0 or enemy.rect.left > WIDTH or
                    enemy.rect.bottom < 0 or enemy.rect.top > HEIGHT):
                    enemy.kill()
                    
            score += 1
            
            # Draw sprites
            all_sprites.draw(screen)
            
        else:
            # Game Over state
            screen.fill(BLACK)
            matrix_rain.draw(screen)
            
            # Draw game over text and scores
            font_large = pygame.font.Font(None, 42)
            font_small = pygame.font.Font(None, 23)
            
            game_over_text = font_large.render('Game Over', True, (255, 0, 0))
            score_text = font_large.render(f'Your Score: {score}', True, (255, 255, 255))
            
            # Update highscore
            startup.save_highscore(player_name, score)
            
            # Create play again and exit text
            play_again_text = font_small.render("Press ENTER to Play Again", True, (0, 255, 0))
            exit_text = font_small.render("Press ESC to Quit", True, (0, 255, 0))
            
            # Draw game over text
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//4 + 80))
            
            # Draw top 3 scores with more spacing
            top_scores = startup.get_top_scores(3)  # Only get top 3
            title_text = font_small.render("Top Hackers:", True, (0, 255, 0))
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 30))
            
            for i, (name, highscore) in enumerate(top_scores):
                color = (0, 255, 0) if name == player_name and score == highscore else (255, 255, 255)
                score_text = font_small.render(f"{i+1}. {name}: {highscore}", True, color)
                y_pos = HEIGHT//2 + (i * 45)  # More spacing between scores
                screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, y_pos))
            
            # Draw play again and exit prompts with more spacing
            screen.blit(play_again_text, (WIDTH//2 - play_again_text.get_width()//2, HEIGHT - 120))
            screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT - 70))
            
            # Handle game over input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_RETURN:
                        return True  # Signal to restart the game
        
        pygame.display.flip()
        clock.tick(60)
    
    return False

if __name__ == "__main__":
    while True:
        if not run_game():
            break
    pygame.quit()

from matrix_rain import MatrixRain  # Import the Matrix effect
from player import Player
from player import Fireball
from player import Doppelganger
from upgrade import MatrixAbilitySystem

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        
        # Load images
        self.walk_sprite_sheet = pygame.image.load("Walk.png").convert_alpha()
        self.idle_sprite_sheet = pygame.image.load("Idle.png").convert_alpha()
        self.punch_sprite_sheet = pygame.image.load("Attack.png").convert_alpha()
        self.fire_image = pygame.image.load("fire.png").convert_alpha()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        
        # Create player and set its sprite group
        self.player = Player(self.walk_sprite_sheet, self.idle_sprite_sheet, self.punch_sprite_sheet)
        self.player.all_sprites = self.all_sprites
        self.all_sprites.add(self.player)

        # Initialize ability system
        self.ability_system = MatrixAbilitySystem(self.screen)
        
        # Game state
        self.paused = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.ability_system.selection_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_ability = self.ability_system.handle_selection(pygame.mouse.get_pos())
                    if selected_ability:
                        print(f"Unlocked: {selected_ability}")
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and self.ability_system.abilities['fireball'].unlocked:
                mouse_pos = pygame.mouse.get_pos()
                fireball = Fireball(self.player.rect.center, mouse_pos, self.fire_image)
                self.fireballs.add(fireball)
                self.all_sprites.add(fireball)
                self.player.punch()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.ability_system.abilities['doppelganger'].unlocked:
                    self.player.create_doppelganger()
                elif event.key == pygame.K_t and self.ability_system.abilities['teleport'].unlocked:
                    mouse_pos = pygame.mouse.get_pos()
                    self.player.trigger_teleport(mouse_pos)

        return True

    def run(self):
        running = True
        while running:
            # Check for ability unlocks
            if self.ability_system.check_unlock_time():
                self.paused = True

            # Handle input
            running = self.handle_input()

            # Update game state if not paused
            if not self.ability_system.selection_active:
                self.all_sprites.update()
                self.player.teleport_distortions.update()

            # Draw
            self.screen.fill((0, 0, 0))
            self.all_sprites.draw(self.screen)
            self.player.teleport_distortions.draw(self.screen)

            # Draw ability unlock screen if active
            if self.ability_system.selection_active:
                self.ability_system.draw_unlock_screen()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

