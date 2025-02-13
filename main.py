# main.py
import pygame
import random
import os

from matrix_rain import MatrixRain
from enemy import Enemy
from platforms import Platform, StartPlatform  # Updated import
from startscreen import StartupScreen
from player import Player, Fireball
from upgrade import MatrixAbilitySystem

class StartPlatform(Platform):
    def __init__(self, screen_width):
        super().__init__(screen_width)
        self.rect.centerx = screen_width // 2
        self.rect.y = 500  # Position slightly higher
        self.speed = 0
        self.has_jumped = False

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Matrix Jump Game")
        self.clock = pygame.time.Clock()
        
        # Load sprite sheets
        try:
            self.walk_sprite_sheet = pygame.image.load(os.path.join("gone_rogue", "Walk.png")).convert_alpha()
            self.idle_sprite_sheet = pygame.image.load(os.path.join("gone_rogue", "Idle.png")).convert_alpha()
            self.punch_sprite_sheet = pygame.image.load(os.path.join("gone_rogue", "Attack.png")).convert_alpha()
            self.fire_image = pygame.image.load(os.path.join("gone_rogue", "fire.png")).convert_alpha()
        except pygame.error as e:
            print(f"Error loading images: {e}")
            pygame.quit()
            return
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.fireballs = pygame.sprite.Group()
        
        # Initialize game systems
        self.ability_system = MatrixAbilitySystem(self.screen)
        self.matrix_rain = MatrixRain(self.WIDTH, self.HEIGHT)
        self.startup = StartupScreen(self.screen, self.WIDTH, self.HEIGHT)
        
        # Game state
        self.player_name = None
        self.player = None
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # Spawn timers
        self.enemy_spawn_timer = 0
        self.platform_spawn_timer = 0
        self.enemy_spawn_delay = 120
        self.platform_spawn_delay = 60
        
        # Game settings
        self.PLATFORM_SPAWN_HEIGHT_MIN = 100
        self.PLATFORM_SPAWN_HEIGHT_MAX = 500
        self.STARTING_PLATFORM_HEIGHT = 500

    def init_game(self):
        """Initialize or reset the game state"""
        # Show startup screen and get player name
        self.player_name = self.startup.show()
        if self.player_name is None:
            return False
            
        # Reset sprite groups
        self.all_sprites.empty()
        self.enemies.empty()
        self.platforms.empty()
        self.fireballs.empty()
        
        # Create starting platform
        initial_platform = StartPlatform(self.WIDTH)
        initial_platform.rect.centerx = self.WIDTH // 2
        initial_platform.rect.y = self.STARTING_PLATFORM_HEIGHT
        self.all_sprites.add(initial_platform)
        self.platforms.add(initial_platform)

        # Create player on starting platform
        self.player = Player(self.walk_sprite_sheet, self.idle_sprite_sheet, 
                           self.punch_sprite_sheet)
        self.player.rect.bottom = initial_platform.rect.top
        self.player.rect.centerx = initial_platform.rect.centerx
        self.player.all_sprites = self.all_sprites
        self.all_sprites.add(self.player)
        
        # Reset game state
        self.score = 0
        self.game_over = False
        self.paused = False
        self.enemy_spawn_timer = 0
        self.platform_spawn_timer = 0
        
        return True

    def handle_input(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return self.init_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    # Handle ability activations
                    if event.key == pygame.K_p and self.ability_system.abilities['doppelganger'].unlocked:
                        self.player.create_doppelganger()
                    elif event.key == pygame.K_t and self.ability_system.abilities['teleport'].unlocked:
                        mouse_pos = pygame.mouse.get_pos()
                        self.player.trigger_teleport(mouse_pos)
                    elif event.key == pygame.K_s:
                        self.player.activate_shield()
                    elif event.key == pygame.K_d:
                        self.player.digital_dash()
                    elif event.key == pygame.K_c:
                        self.player.code_burst()
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.ability_system.selection_active:
                        selected_ability = self.ability_system.handle_selection(pygame.mouse.get_pos())
                        if selected_ability:
                            print(f"Unlocked: {selected_ability}")
                    elif self.ability_system.abilities['fireball'].unlocked:
                        mouse_pos = pygame.mouse.get_pos()
                        fireball = Fireball(self.player.rect.center, mouse_pos, self.fire_image)
                        self.fireballs.add(fireball)
                        self.all_sprites.add(fireball)
                        self.player.punch()
        
        return True

    def spawn_enemies(self):
        """Handle enemy spawning"""
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            self.enemy_spawn_timer = 0
            enemy = Enemy(self.WIDTH, self.HEIGHT)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def spawn_platforms(self):
        """Handle platform spawning"""
        self.platform_spawn_timer += 1
        if self.platform_spawn_timer >= self.platform_spawn_delay:
            self.platform_spawn_timer = 0
            platform = Platform(self.WIDTH)
            platform.rect.y = random.randint(self.PLATFORM_SPAWN_HEIGHT_MIN, 
                                          self.PLATFORM_SPAWN_HEIGHT_MAX)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

    def update(self):
        """Update game state"""
        if not self.game_over and not self.paused:
            # Spawn enemies and platforms
            self.spawn_enemies()
            self.spawn_platforms()
            
            # Check for ability unlocks
            if self.ability_system.check_unlock_time():
                self.paused = True
                
            # Update all sprites if not paused
            if not self.ability_system.selection_active:
                self.all_sprites.update()
                self.player.teleport_distortions.update()
                
                # Handle platform collisions
                self.player.handle_platform_collision(self.platforms)
                
                # Check if player fell off screen
                if self.player.rect.top > self.HEIGHT:
                    self.game_over = True
                
                # Check enemy collisions
                if pygame.sprite.spritecollide(self.player, self.enemies, False):
                    if not self.player.shield_active:
                        self.game_over = True
                    
                # Check fireball hits on enemies
                for fireball in self.fireballs:
                    enemies_hit = pygame.sprite.spritecollide(fireball, self.enemies, True)
                    if enemies_hit:
                        fireball.kill()
                        self.score += 10  # Bonus points for hitting enemies
                
                # Update score
                self.score += 1
                
            # Clean up off-screen sprites
            self.cleanup_sprites()

    def cleanup_sprites(self):
        """Remove sprites that have moved off screen"""
        for sprite in self.platforms:
            if (sprite.direction == -1 and sprite.rect.left > self.WIDTH) or \
               (sprite.direction == 1 and sprite.rect.right < 0):
                sprite.kill()
        for enemy in self.enemies:
            if (enemy.rect.right < 0 or enemy.rect.left > self.WIDTH or
                enemy.rect.bottom < 0 or enemy.rect.top > self.HEIGHT):
                enemy.kill()
        for fireball in self.fireballs:
            if (fireball.rect.right < 0 or fireball.rect.left > self.WIDTH or
                fireball.rect.bottom < 0 or fireball.rect.top > self.HEIGHT):
                fireball.kill()

    def draw(self):
        """Draw the game state"""
        self.screen.fill((0, 0, 0))  # Black background
        self.matrix_rain.draw(self.screen)
        
        if not self.game_over:
            self.all_sprites.draw(self.screen)
            self.player.teleport_distortions.draw(self.screen)
            
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, (0, 255, 0))
            self.screen.blit(score_text, (10, 10))
            
            if self.ability_system.selection_active:
                self.ability_system.draw_unlock_screen()
        else:
            self.draw_game_over()

    def draw_game_over(self):
        """Draw the game over screen"""
        font_large = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 23)
        
        # Draw game over text
        game_over_text = font_large.render('Game Over', True, (255, 0, 0))
        score_text = font_large.render(f'Your Score: {self.score}', True, (255, 255, 255))
        
        self.startup.save_highscore(self.player_name, self.score)
        
        screen_center = self.WIDTH // 2
        self.screen.blit(game_over_text, 
                        (screen_center - game_over_text.get_width()//2, self.HEIGHT//4))
        self.screen.blit(score_text, 
                        (screen_center - score_text.get_width()//2, self.HEIGHT//4 + 80))
        
        # Draw top scores
        top_scores = self.startup.get_top_scores(3)
        title_text = font_small.render("Top Hackers:", True, (0, 255, 0))
        self.screen.blit(title_text, 
                        (screen_center - title_text.get_width()//2, self.HEIGHT//2 - 30))
        
        for i, (name, highscore) in enumerate(top_scores):
            color = (0, 255, 0) if name == self.player_name and self.score == highscore else (255, 255, 255)
            score_text = font_small.render(f"{i+1}. {name}: {highscore}", True, color)
            y_pos = self.HEIGHT//2 + (i * 45)
            self.screen.blit(score_text, 
                           (screen_center - score_text.get_width()//2, y_pos))
        
        # Draw restart prompts
        play_again = font_small.render("Press ENTER to Play Again", True, (0, 255, 0))
        exit_text = font_small.render("Press ESC to Quit", True, (0, 255, 0))
        
        self.screen.blit(play_again, 
                        (screen_center - play_again.get_width()//2, self.HEIGHT - 120))
        self.screen.blit(exit_text, 
                        (screen_center - exit_text.get_width()//2, self.HEIGHT - 70))

    def run(self):
        """Main game loop"""
        if not self.init_game():
            return
            
        running = True
        while running:
            running = self.handle_input()
            if not running:
                break
                
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()