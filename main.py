import pygame
import random
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