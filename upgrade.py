import pygame
import random
class MatrixAbilitySystem:
    def __init__(self, screen):
        self.screen = screen
        self.abilities = {
            'fireball': Ability('Fireball', 'Launch a destructive fireball at enemies'),
            'teleport': Ability('Teleport', 'Instantly teleport to cursor position'),
            'doppelganger': Ability('Doppelganger', 'Create a temporary clone')
        }
        self.selection_active = False
        self.current_score = 0
        self.points_per_unlock = 3000
        self.unlocks_available = 0
        self.unlocks_used = 0


        try:
            self.font_large = pygame.font.Font("matrix_font.ttf", 48)
            self.font_medium = pygame.font.Font("matrix_font.ttf", 36)
            self.font_small = pygame.font.Font("matrix_font.ttf", 24)
        except:
            self.font_large = pygame.font.SysFont("couriernew", 48)
            self.font_medium = pygame.font.SysFont("couriernew", 36)
            self.font_small = pygame.font.SysFont("couriernew", 24)


        self.COLOR_MATRIX_GREEN = (0, 255, 0)
        self.COLOR_DARK_GREEN = (0, 100, 0)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_HIGHLIGHT = (200, 255, 200)
        
        # Matrix rain effect
        self.matrix_chars = [chr(i) for i in range(33, 127)]
        self.rain_drops = []
        self.init_rain_drops()
        
        # Scanning line effect
        self.scan_line_pos = 0
        self.scan_line_speed = 5

    def check_unlock_score(self, current_score):
        """Check if new abilities should be unlocked based on score"""
        self.current_score = current_score
        potential_unlocks = current_score // self.points_per_unlock
        new_unlocks = potential_unlocks - self.unlocks_used
        
        if new_unlocks > 0 and not self.selection_active:
            self.unlocks_available = new_unlocks
            self.selection_active = True
            return True
        return False

    def handle_selection(self, mouse_pos):
        """Handle ability selection"""
        if not self.selection_active:
            return None

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Calculate ability card positions
        card_width = 200
        card_height = 100
        spacing = 50
        total_width = (len(self.abilities) * card_width) + ((len(self.abilities) - 1) * spacing)
        start_x = (screen_width - total_width) // 2
        y = (screen_height - card_height) // 2

        for i, (ability_name, ability) in enumerate(self.abilities.items()):
            if ability.unlocked:
                continue

            card_x = start_x + (i * (card_width + spacing))
            card_rect = pygame.Rect(card_x, y, card_width, card_height)

            if card_rect.collidepoint(mouse_pos):
                ability.unlocked = True
                self.unlocks_used += 1
                
                if self.unlocks_available > 1:
                    self.unlocks_available -= 1
                else:
                    self.selection_active = False
                    self.unlocks_available = 0
                
                return ability_name
        return None
    

    def init_rain_drops(self):
        for _ in range(50):  # Number of rain drops
            self.rain_drops.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'speed': random.randint(5, 15)
            })

    def update_rain_drops(self):
        for drop in self.rain_drops:
            drop['y'] += drop['speed']
            if drop['y'] > 600:
                drop['y'] = 0
                drop['x'] = random.randint(0, 800)

    def draw_matrix_rain(self, surface):
        for drop in self.rain_drops:
            char = random.choice(self.matrix_chars)
            color = (0, random.randint(150, 255), 0)
            text = self.font_small.render(char, True, color)
            surface.blit(text, (drop['x'], drop['y']))

    def draw_unlock_screen(self):
        """Draw the ability unlock screen"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        # Setup dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        card_width = 200
        card_height = 100
        spacing = 50

        # Draw header
        font = pygame.font.Font(None, 36)
        header_text = f"New Ability Unlock Available! (Score: {self.current_score})"
        header = font.render(header_text, True, (0, 255, 0))
        header_pos = ((screen_width - header.get_width()) // 2, screen_height // 4)
        self.screen.blit(header, header_pos)

        # Calculate total width of all cards
        total_width = (len(self.abilities) * card_width) + ((len(self.abilities) - 1) * spacing)
        start_x = (screen_width - total_width) // 2
        y = (screen_height - card_height) // 2

        # Draw ability cards
        for i, (ability_name, ability) in enumerate(self.abilities.items()):
            if ability.unlocked:
                continue

            card_x = start_x + (i * (card_width + spacing))
            
            # Draw card background with green border
            pygame.draw.rect(self.screen, (0, 0, 0), (card_x, y, card_width, card_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (card_x, y, card_width, card_height), 2)

            # Draw ability name
            name_text = font.render(ability.name, True, (0, 255, 0))
            name_pos = (card_x + (card_width - name_text.get_width()) // 2, y + 20)
            self.screen.blit(name_text, name_pos)

            # Draw ability description
            desc_font = pygame.font.Font(None, 24)
            desc_text = desc_font.render(ability.description, True, (0, 255, 0))
            desc_pos = (card_x + (card_width - desc_text.get_width()) // 2, y + 60)
            self.screen.blit(desc_text, desc_pos)

class Ability:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.unlocked = False


