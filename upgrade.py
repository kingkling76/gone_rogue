import pygame
import random
class Ability:
    def __init__(self, name, description, icon=None):
        self.name = name
        self.description = description
        self.icon = icon
        self.unlocked = False

class MatrixAbilitySystem:
    def __init__(self, screen):
        self.screen = screen
        self.abilities = {
            'fireball': Ability('Fireball.exe', 'Execute: Launch destructive data packet'),
            'teleport': Ability('Teleport.sys', 'System: Override spatial coordinates'),
            'doppelganger': Ability('Clone.dll', 'Process: Generate autonomous instance'),
            # New abilities
            'time_slow': Ability('TimeDilation.exe', 'System: Manipulate local time variables'),
            'matrix_vision': Ability('Decrypt.sys', 'Execute: Reveal system vulnerabilities'),
            'wall_run': Ability('GravityHack.dll', 'Override: Manipulate local gravity vectors'),
            'data_shield': Ability('Firewall.sys', 'Defense: Generate damage nullification field'),
            'code_burst': Ability('Surge.exe', 'Attack: Release omnidirectional energy pulse'),
            'system_hack': Ability('Control.dll', 'Hack: Temporarily control nearby enemies'),
            'digital_dash': Ability('Phase.sys', 'Movement: Quick forward data transmission'),
            'recursive_clone': Ability('Recursion.exe', 'Generate: Create clone that can also clone')
        }
        
        # Timing for unlocks (in milliseconds)
        self.unlock_times = [10000, 20000, 30000, 40000]
        self.next_unlock_index = 0
        self.selection_active = False
        self.game_start_time = pygame.time.get_ticks()
        
        # Load Matrix-style font (fallback to monospace system font if custom font not available)
        try:
            self.font_large = pygame.font.Font("matrix_font.ttf", 48)
            self.font_medium = pygame.font.Font("matrix_font.ttf", 36)
            self.font_small = pygame.font.Font("matrix_font.ttf", 24)
        except:
            self.font_large = pygame.font.SysFont("couriernew", 48)
            self.font_medium = pygame.font.SysFont("couriernew", 36)
            self.font_small = pygame.font.SysFont("couriernew", 24)
        
        # Matrix color scheme
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
        if not self.selection_active:
            return

        # Create main surface with alpha
        main_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        main_surface.fill((0, 0, 0, 230))

        # Draw matrix rain
        self.update_rain_drops()
        self.draw_matrix_rain(main_surface)

        # Draw scanning line
        scan_line = pygame.Surface((800, 2), pygame.SRCALPHA)
        scan_line.fill((0, 255, 0, 100))
        self.scan_line_pos = (self.scan_line_pos + self.scan_line_speed) % 600
        main_surface.blit(scan_line, (0, self.scan_line_pos))

        # Draw title with "typing" effect
        title = "SYSTEM UPGRADE AVAILABLE"
        title_surface = self.font_large.render(title, True, self.COLOR_MATRIX_GREEN)
        title_rect = title_surface.get_rect(center=(400, 100))
        main_surface.blit(title_surface, title_rect)

        # Draw available abilities
        available_abilities = self.get_available_abilities()
        button_height = 80
        spacing = 20
        start_y = 200

        mouse_pos = pygame.mouse.get_pos()
        
        for i, ability in enumerate(available_abilities):
            button_rect = pygame.Rect(200, start_y + i * (button_height + spacing), 400, button_height)
            
            # Check for hover
            if button_rect.collidepoint(mouse_pos):
                # Draw "selected" effect
                pygame.draw.rect(main_surface, self.COLOR_DARK_GREEN, button_rect)
                pygame.draw.rect(main_surface, self.COLOR_MATRIX_GREEN, button_rect, 2)
                
                # Draw glitch effect
                if random.random() < 0.1:
                    glitch_offset = random.randint(-2, 2)
                    pygame.draw.rect(main_surface, self.COLOR_HIGHLIGHT, 
                                   button_rect.inflate(glitch_offset, 0), 1)
            else:
                pygame.draw.rect(main_surface, self.COLOR_BLACK, button_rect)
                pygame.draw.rect(main_surface, self.COLOR_DARK_GREEN, button_rect, 1)

            # Draw ability name with console-style prefix
            name_text = self.font_medium.render(f"> {ability.name}", True, self.COLOR_MATRIX_GREEN)
            name_rect = name_text.get_rect(topleft=(button_rect.left + 10, button_rect.top + 10))
            main_surface.blit(name_text, name_rect)

            # Draw description with terminal-style formatting
            desc_text = self.font_small.render(f"  [{ability.description}]", True, self.COLOR_MATRIX_GREEN)
            desc_rect = desc_text.get_rect(topleft=(button_rect.left + 10, button_rect.top + 45))
            main_surface.blit(desc_text, desc_rect)

        # Draw "Matrix code" in the background of each button
        for x in range(200, 600, 20):
            for y in range(200, 500, 20):
                if random.random() < 0.1:
                    char = random.choice(self.matrix_chars)
                    char_surface = self.font_small.render(char, True, (0, 50, 0))
                    main_surface.blit(char_surface, (x, y))

        # Blit the main surface to the screen
        self.screen.blit(main_surface, (0, 0))

    def get_available_abilities(self):
        return [ability for ability in self.abilities.values() if not ability.unlocked]

    def check_unlock_time(self):
        if self.next_unlock_index >= len(self.unlock_times):
            return False  # No more abilities to unlock

        current_time = pygame.time.get_ticks() - self.game_start_time
        if current_time >= self.unlock_times[self.next_unlock_index]:
            self.selection_active = True
            self.next_unlock_index += 1  # Move to next unlock
            return True
        return False


    def handle_selection(self, mouse_pos):
        if not self.selection_active:
            return None

        available_abilities = self.get_available_abilities()
        button_height = 80
        spacing = 20
        start_y = 200

        for i, ability in enumerate(available_abilities):
            button_rect = pygame.Rect(200, start_y + i * (button_height + spacing), 400, button_height)
            if button_rect.collidepoint(mouse_pos):
                ability.unlocked = True
                self.selection_active = False
                self.next_unlock_index += 1
                return ability.name
        
        return None
