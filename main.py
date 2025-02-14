# main.py
import pygame
import random
import os
import time

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

def draw_health_bar(surface, current_health, max_health):
    bar_x, bar_y = 20, 10  
    bar_width, bar_height = 200, 15  

    health_ratio = current_health / max_health
    filled_width = int(bar_width * health_ratio)

    # Outer glowing effect (green border)
    pygame.draw.rect(surface, (0, 255, 0), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)

    # Background bar (black)
    pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))

    # Foreground bar (glowing green, reduced brightness as health drops)
    green_intensity = int(255 * health_ratio)
    pygame.draw.rect(surface, (0, green_intensity, 0), (bar_x, bar_y, filled_width, bar_height))

    # Digital "glitch" effect: draw small green flickering pixels randomly in the bar
    if random.random() < 0.2:  # 20% chance to draw a glitch
        glitch_x = random.randint(bar_x, bar_x + filled_width)
        glitch_y = random.randint(bar_y, bar_y + bar_height)
        pygame.draw.rect(surface, (0, 255, 0), (glitch_x, glitch_y, 2, 2))

    # Render health percentage in a "Matrix" style font
    font = pygame.font.Font(None, 20)
    health_text = font.render(f'{int(health_ratio * 100)}%', True, (0, 255, 0))
    surface.blit(health_text, (bar_x + bar_width + 10, bar_y - 2))

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
            self.walk_sprite_sheet = pygame.image.load("Walk.png")
            self.idle_sprite_sheet = pygame.image.load("Idle.png")
            self.punch_sprite_sheet = pygame.image.load( "Attack.png")
            self.fire_image = pygame.image.load("fire.png")
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
        self.fireball_charges = 3
        self.teleport_charges = 3
        self.fireball_last_used = time.time()  # Initialize with current time
        self.teleport_last_used = time.time()  # Initialize with current time# Timestamp for the last teleport use

        # Recharge cooldowns in seconds
        self.recharge_time = 4

        # Set initial positions for the recharge bars
        self.fireball_bar_x = 20
        self.fireball_bar_y = 40
        self.teleport_bar_x = 20
        self.teleport_bar_y = 70
        

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
                if self.fireball_charges > 0:  # Check if charges are available
                    mouse_pos = pygame.mouse.get_pos()
                    fireball = Fireball(self.player.rect.center, mouse_pos, self.fire_image)
                    self.fireballs.add(fireball)
                    self.all_sprites.add(fireball)
                    self.player.punch()
                    # Consume a charge and update last used time
                    self.fireball_charges -= 1
                    self.fireball_last_used = time.time()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and self.ability_system.abilities['doppelganger'].unlocked:
                    self.player.create_doppelganger()
                elif event.key == pygame.K_t and self.ability_system.abilities['teleport'].unlocked:
                    if self.teleport_charges > 0:  # Check if charges are available
                        mouse_pos = pygame.mouse.get_pos()
                        self.player.trigger_teleport(mouse_pos)
                        # Consume a charge and update last used time
                        self.teleport_charges -= 1
                        self.teleport_last_used = time.time()

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
            draw_health_bar(self.screen, self.player.current_health, self.player.max_health)

            # Handle ability recharges
            current_time = time.time()

            # Recharge fireball ability
            if self.fireball_charges < 3:
                time_since_last_fireball = current_time - self.fireball_last_used
                if time_since_last_fireball >= self.recharge_time:
                    self.fireball_charges += 1
                    self.fireball_last_used = current_time - (time_since_last_fireball - self.recharge_time)

            # Recharge teleport ability
            if self.teleport_charges < 3:
                time_since_last_teleport = current_time - self.teleport_last_used
                if time_since_last_teleport >= self.recharge_time:
                    self.teleport_charges += 1
                    self.teleport_last_used = current_time - (time_since_last_teleport - self.recharge_time)
            
            # Check for ability unlocks
            if self.ability_system.check_unlock_time():
                self.paused = False
                
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
                        self.game_over = False
                    
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


    def draw_ability_ui(self):
        """Draw Matrix-themed UI elements for abilities in screen corners"""
        current_time = time.time()
        
        def draw_hexagonal_frame(surface, x, y, width, height, color, thickness=2):
            """Draw a hexagonal frame around a UI element"""
            points = [
                (x + 10, y),            # Top
                (x + width - 10, y),    # Top right
                (x + width, y + height/2),  # Middle right
                (x + width - 10, y + height),  # Bottom right
                (x + 10, y + height),   # Bottom left
                (x, y + height/2),      # Middle left
            ]
            pygame.draw.polygon(surface, color, points, thickness)
            
            # Add glowing effect
            for i in range(2):
                glow_points = [(px + random.randint(-1, 1), py + random.randint(-1, 1)) for px, py in points]
                pygame.draw.polygon(surface, (0, 255, 0, 50), glow_points, 1)

        def draw_ability_slot(x, y, icon_char, charges, last_used, is_unlocked, align_right=False):
            if not is_unlocked:
                return
                
            slot_width = 250
            slot_height = 60
            
            if align_right:
                x = x - slot_width  # Adjust x position for right alignment
            
            # Draw main container with glow effect
            for offset in range(2):
                pygame.draw.rect(self.screen, (0, 255, 0, 50),
                            (x - offset, y - offset, slot_width + offset*2, slot_height + offset*2), 1)
            
            # Draw hexagonal frame
            draw_hexagonal_frame(self.screen, x, y, slot_width, slot_height, (0, 255, 0))
            
            # Draw digital-style icon
            font_large = pygame.font.Font(None, 40)
            icon_text = font_large.render(icon_char, True, (0, 255, 0))
            self.screen.blit(icon_text, (x + 15, y + slot_height//2 - 15))
            
            # Draw charges as Matrix-style indicators
            for i in range(3):
                charge_color = (0, 255, 0) if i < charges else (0, 50, 0)
                charge_rect = pygame.Rect(x + 60 + i*20, y + 10, 10, 10)
                pygame.draw.rect(self.screen, charge_color, charge_rect)
                # Add digital glitch effect to active charges
                if i < charges and random.random() < 0.1:
                    pygame.draw.rect(self.screen, (0, 255, 255), charge_rect)
            
            # Draw recharge bar with digital effect
            if charges < 3:
                fill_ratio = min((current_time - last_used) / self.recharge_time, 1)
                bar_width = 120
                bar_height = 8
                bar_x = x + 60
                bar_y = y + slot_height - 20
                
                # Background bar
                pygame.draw.rect(self.screen, (0, 50, 0), (bar_x, bar_y, bar_width, bar_height))
                
                # Filled portion with scanline effect
                filled_width = int(bar_width * fill_ratio)
                if filled_width > 0:
                    pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))
                    # Add scanline effect
                    for i in range(0, bar_height, 2):
                        pygame.draw.line(self.screen, (0, 200, 0), 
                                    (bar_x, bar_y + i),
                                    (bar_x + filled_width, bar_y + i))
                
                # Digital percentage display
                percent_text = font_large.render(f"{int(fill_ratio * 100)}%", True, (0, 255, 0))
                self.screen.blit(percent_text, (bar_x + bar_width + 10, bar_y - 5))

        def draw_doppelganger_slot(x, y, is_unlocked):
            if not is_unlocked:
                return
                
            slot_width = 250
            slot_height = 60
            
            x = x - slot_width  # Adjust x position for right alignment
            
            # Draw main container with different color scheme
            for offset in range(2):
                pygame.draw.rect(self.screen, (0, 200, 200, 50),
                            (x - offset, y - offset, slot_width + offset*2, slot_height + offset*2), 1)
            
            # Draw hexagonal frame with cyan color
            draw_hexagonal_frame(self.screen, x, y, slot_width, slot_height, (0, 200, 200))
            
            # Draw terminal-style command
            font = pygame.font.Font(None, 36)
            command_text = font.render("./doppelganger", True, (0, 200, 200))
            self.screen.blit(command_text, (x + 20, y + slot_height//2 - 15))
            
            # Add blinking cursor effect
            if time.time() % 1 > 0.5:  # Blink every half second
                cursor_x = x + 20 + command_text.get_width() + 5
                pygame.draw.rect(self.screen, (0, 200, 200), 
                            (cursor_x, y + slot_height//2 - 12, 8, 20))
            
            # Add digital noise effect
            if random.random() < 0.05:
                for _ in range(3):
                    noise_x = x + random.randint(0, slot_width)
                    noise_y = y + random.randint(0, slot_height)
                    pygame.draw.rect(self.screen, (0, 255, 255), 
                                (noise_x, noise_y, 2, 2))

        # Define corner margins
        margin = 20
        bottom_offset = 100  # Distance from bottom of screen
        
        # Draw Fireball ability slot in bottom left corner
        draw_ability_slot(
            margin,
            self.HEIGHT - bottom_offset,
            "⌾",
            self.fireball_charges,
            self.fireball_last_used,
            self.ability_system.abilities['fireball'].unlocked,
            align_right=False
        )
        
        # Draw Teleport ability slot in bottom right corner
        draw_ability_slot(
            self.WIDTH - margin,
            self.HEIGHT - bottom_offset,
            "⌖",
            self.teleport_charges,
            self.teleport_last_used,
            self.ability_system.abilities['teleport'].unlocked,
            align_right=True
        )
        
        # Draw Doppelganger ability slot in top right corner
        draw_doppelganger_slot(
            self.WIDTH - margin,
            margin,
            self.ability_system.abilities['doppelganger'].unlocked
        )
        
        # Add random Matrix-style characters in corners
        if random.random() < 0.1:
            matrix_chars = "01"
            font_small = pygame.font.Font(None, 20)
            for corner in range(3):  # Add effects for all three corners
                char_text = font_small.render(random.choice(matrix_chars), True, (0, 255, 0))
                if corner == 0:  # Bottom left
                    x = random.randint(margin, margin + 250)
                    y = random.randint(self.HEIGHT - bottom_offset - 20, self.HEIGHT - bottom_offset + 60)
                elif corner == 1:  # Bottom right
                    x = random.randint(self.WIDTH - 270, self.WIDTH - margin)
                    y = random.randint(self.HEIGHT - bottom_offset - 20, self.HEIGHT - bottom_offset + 60)
                else:  # Top right
                    x = random.randint(self.WIDTH - 270, self.WIDTH - margin)
                    y = random.randint(margin - 20, margin + 60)
                self.screen.blit(char_text, (x, y))
    def draw(self):
        """Draw the game state"""
        self.screen.fill((0, 0, 0))  # Black background
        self.matrix_rain.draw(self.screen)

        if not self.game_over:
            self.all_sprites.draw(self.screen)
            self.player.teleport_distortions.draw(self.screen)
            
            # Draw health bar here
            draw_health_bar(self.screen, self.player.current_health, self.player.max_health)
            self.draw_ability_ui()
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {self.score}', True, (0, 255, 0))
            self.screen.blit(score_text, (10, 40))  # Adjusted position to avoid overlap with the health bar
            
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