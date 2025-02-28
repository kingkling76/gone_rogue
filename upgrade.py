import pygame
import random
import math
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
        self.max_upgrades =3


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
        
        if new_unlocks > 0 and not self.selection_active and self.unlocks_used<3:
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

            if self.unlocks_used==3:
                return None


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
        """Draw a visually impressive ability unlock screen with animations and effects"""
        current_time = pygame.time.get_ticks()
        animation_duration = 1500  # Animation duration in milliseconds
        
        # Create gradient background overlay instead of flat black
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        for y in range(self.screen.get_height()):
            alpha = 220 - (y * 40 / self.screen.get_height())
            overlay.fill((5, 10, 20), (0, y, self.screen.get_width(), 1))
        overlay.set_alpha(230)
        self.screen.blit(overlay, (0, 0))
        
        # Add particles/stars in background
        if not hasattr(self, 'particles'):
            self.particles = [(random.randint(0, self.screen.get_width()), 
                            random.randint(0, self.screen.get_height()),
                            random.randint(1, 3)) for _ in range(100)]
        
        for i, (x, y, size) in enumerate(self.particles):
            # Make particles pulse
            pulse = abs(math.sin(current_time / 500 + i * 0.1)) * 0.7 + 0.3
            color = (int(50 * pulse), int(180 * pulse), int(255 * pulse))
            pygame.draw.circle(self.screen, color, (x, y), size)
            # Move particles slightly for animation
            self.particles[i] = ((x + math.sin(current_time / 1000 + i) * 0.5) % self.screen.get_width(), 
                            (y + math.cos(current_time / 1200 + i) * 0.5) % self.screen.get_height(),
                            size)
        
        # Setup dimensions
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        card_width = 250
        card_height = 180
        spacing = 40
        
        # Draw glowing magical circle
        circle_radius = min(screen_width, screen_height) * 0.35
        circle_center = (screen_width // 2, screen_height // 2)
        
        # Draw multiple circles with decreasing alpha for glow effect
        for r in range(int(circle_radius), int(circle_radius - 30), -1):
            alpha = 100 - (circle_radius - r) * 3
            circle_color = (0, int(100 + (circle_radius - r) * 5), int(150 + (circle_radius - r) * 3), int(alpha))
            circle_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, circle_color, (r, r), r, 2)
            
            # Make the circle pulse
            pulse_scale = 1.0 + 0.03 * math.sin(current_time / 500)
            scaled_r = r * pulse_scale
            circle_surf = pygame.transform.scale(circle_surf, (int(scaled_r * 2), int(scaled_r * 2)))
            
            self.screen.blit(circle_surf, (circle_center[0] - scaled_r, circle_center[1] - scaled_r))
        
        # Draw magical runes/symbols around the circle
        num_runes = 8
        rune_radius = circle_radius + 20
        rune_size = 15
        
        for i in range(num_runes):
            angle = 2 * math.pi * i / num_runes + (current_time / 4000)
            x = circle_center[0] + math.cos(angle) * rune_radius
            y = circle_center[1] + math.sin(angle) * rune_radius
            
            # Draw a glowing rune
            rune_color = (0, 255, 200)
            pygame.draw.rect(self.screen, rune_color, (x - rune_size // 2, y - rune_size // 2, rune_size, rune_size))
            glow = pygame.Surface((rune_size * 3, rune_size * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 255, 200, 50), (rune_size * 3 // 2, rune_size * 3 // 2), rune_size)
            self.screen.blit(glow, (x - rune_size * 3 // 2, y - rune_size * 3 // 2))
        
        # Draw header with custom font (fallback to default if custom fails)
        try:
            header_font = pygame.font.Font("fonts/ethnocentric.ttf", 36)
        except:
            header_font = pygame.font.Font(None, 42)
        
        # Create a gradient text effect for the header
        header_text = f"NEW ABILITY UNLOCKED"
        header_surf = pygame.Surface((800, 100), pygame.SRCALPHA)
        
        # Draw multiple versions of text with offset for glow effect
        for offset in range(5, 0, -1):
            glow_text = header_font.render(header_text, True, (0, 255 // offset, 150 // offset))
            header_surf.blit(glow_text, (offset, offset))
        
        # Main text on top
        main_text = header_font.render(header_text, True, (50, 255, 200))
        header_surf.blit(main_text, (0, 0))
        
        # Position and render the header
        header_pos = ((screen_width - main_text.get_width()) // 2, screen_height // 5)
        self.screen.blit(header_surf, (header_pos[0] - 5, header_pos[0] - 5))
        
        # Render score with a more dynamic effect
        score_font = pygame.font.Font(None, 32)
        score_text = f"CURRENT SCORE: {self.current_score}"
        score_surf = score_font.render(score_text, True, (220, 220, 100))
        score_glow = score_font.render(score_text, True, (120, 120, 50))
        
        # Pulse the score
        score_scale = 1.0 + 0.1 * abs(math.sin(current_time / 300))
        score_width = score_surf.get_width() * score_scale
        score_height = score_surf.get_height() * score_scale
        
        score_pos = ((screen_width - score_width) // 2, header_pos[1] + 60)
        
        # Draw glow behind score
        self.screen.blit(pygame.transform.scale(score_glow, (int(score_width + 10), int(score_height + 10))), 
                        (score_pos[0] - 5, score_pos[1] - 5))
        # Draw main score
        self.screen.blit(pygame.transform.scale(score_surf, (int(score_width), int(score_height))), score_pos)
        
        # Calculate total width of all cards
        unlocked_abilities = [ability for ability in self.abilities.values() if not ability.unlocked]
        total_width = (len(unlocked_abilities) * card_width) + ((len(unlocked_abilities) - 1) * spacing)
        start_x = (screen_width - total_width) // 2
        y = (screen_height - card_height) // 2
        
        # Draw ability cards with floating animation and glow effects
        for i, ability in enumerate(unlocked_abilities):
            # Calculate card position with a slight floating animation
            float_offset = math.sin(current_time / 500 + i) * 7
            card_x = start_x + (i * (card_width + spacing))
            card_y = y + float_offset
            
            # Create card surface with transparency
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            
            # Draw card background - gradient from dark blue to lighter blue
            for gradient_y in range(card_height):
                alpha = 230
                blue_val = 30 + gradient_y * 30 // card_height
                pygame.draw.line(card_surf, (10, 20, blue_val, alpha), 
                            (0, gradient_y), (card_width, gradient_y))
            
            # Draw card border with glow effect
            border_width = 3
            # Outer glow
            glow_size = 10
            glow_surf = pygame.Surface((card_width + glow_size * 2, card_height + glow_size * 2), pygame.SRCALPHA)
            glow_rect = pygame.Rect(glow_size, glow_size, card_width, card_height)
            
            # Make the border pulse with time
            pulse = abs(math.sin(current_time / 700 + i * 0.5)) * 0.7 + 0.3
            border_color = (int(60 * pulse), int(200 * pulse), int(180 * pulse))
            
            # Draw multiple rectangles with decreasing alpha for glow
            for offset in range(glow_size, 0, -2):
                alpha = 150 - offset * 10
                pygame.draw.rect(glow_surf, (*border_color, alpha), 
                            glow_rect.inflate(offset, offset), border_width)
            
            # Main border
            pygame.draw.rect(card_surf, border_color, 
                        (0, 0, card_width, card_height), border_width)
            
            # Draw card content
            # Ability icon
            icon_size = 50
            icon_x = (card_width - icon_size) // 2
            icon_y = 20
            
            # Draw a placeholder icon (can be replaced with actual ability icons)
            pygame.draw.circle(card_surf, border_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)
            inner_color = (min(border_color[0] + 50, 255), min(border_color[1] + 50, 255), min(border_color[2] + 50, 255))
            pygame.draw.circle(card_surf, inner_color, (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 3)
            
            # Draw ability name with a stylish effect
            try:
                name_font = pygame.font.Font("fonts/exo2.ttf", 20)
            except:
                name_font = pygame.font.Font(None, 24)
                
            name_text = name_font.render(ability.name.upper(), True, (255, 255, 255))
            name_shadow = name_font.render(ability.name.upper(), True, (50, 100, 100))
            
            # Shadow effect
            name_pos = (card_width - name_text.get_width()) // 2
            card_surf.blit(name_shadow, (name_pos + 2, icon_y + icon_size + 12))
            card_surf.blit(name_text, (name_pos, icon_y + icon_size + 10))
            
            # Draw ability description
            try:
                desc_font = pygame.font.Font("fonts/exo2.ttf", 16)
            except:
                desc_font = pygame.font.Font(None, 18)
            
            # Word wrap the description
            words = ability.description.split(' ')
            desc_y = icon_y + icon_size + 45
            line_height = 20
            line = ""
            
            for word in words:
                test_line = line + word + " "
                test_width = desc_font.size(test_line)[0]
                
                if test_width < card_width - 20:
                    line = test_line
                else:
                    text = desc_font.render(line, True, (200, 200, 200))
                    text_x = (card_width - text.get_width()) // 2
                    card_surf.blit(text, (text_x, desc_y))
                    desc_y += line_height
                    line = word + " "
            
            # Draw the last line
            if line:
                text = desc_font.render(line, True, (200, 200, 200))
                text_x = (card_width - text.get_width()) // 2
                card_surf.blit(text, (text_x, desc_y))
            
            # Draw "Select" button at bottom
            button_width = 100
            button_height = 30
            button_x = (card_width - button_width) // 2
            button_y = card_height - button_height - 15
            
            # Button pulse animation
            pulse = abs(math.sin(current_time / 300 + i * 0.5)) * 0.7 + 0.3
            button_color = (int(10 * pulse), int(150 * pulse), int(100 * pulse))
            
            pygame.draw.rect(card_surf, button_color, 
                        (button_x, button_y, button_width, button_height), 0, 5)
            pygame.draw.rect(card_surf, (200, 255, 200), 
                        (button_x, button_y, button_width, button_height), 2, 5)
            
            button_font = pygame.font.Font(None, 20)
            button_text = button_font.render("SELECT", True, (255, 255, 255))
            button_text_pos = (button_x + (button_width - button_text.get_width()) // 2, 
                            button_y + (button_height - button_text.get_height()) // 2)
            card_surf.blit(button_text, button_text_pos)
            
            # Apply glow and card to screen
            self.screen.blit(glow_surf, (card_x - glow_size, card_y - glow_size))
            self.screen.blit(card_surf, (card_x, card_y))
        
        # Add subtle rays of light emanating from center
        ray_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for angle in range(0, 360, 20):
            rad = math.radians(angle)
            length = min(screen_width, screen_height) * 0.7
            end_x = circle_center[0] + math.cos(rad + current_time / 5000) * length
            end_y = circle_center[1] + math.sin(rad + current_time / 5000) * length
            
            # Draw ray with gradient alpha
            points = []
            for i in range(20):
                dist = i / 20
                width = 10 * (1 - dist)
                perpendicular_x = math.cos(rad + math.pi/2) * width
                perpendicular_y = math.sin(rad + math.pi/2) * width
                
                points.append((
                    circle_center[0] + math.cos(rad) * length * dist + perpendicular_x,
                    circle_center[1] + math.sin(rad) * length * dist + perpendicular_y
                ))
                
                points.insert(0, (
                    circle_center[0] + math.cos(rad) * length * dist - perpendicular_x,
                    circle_center[1] + math.sin(rad) * length * dist - perpendicular_y
                ))
            
            # Fill the ray polygon with a semi-transparent color
            pygame.draw.polygon(ray_surface, (100, 200, 255, 30), points)
        
        # Apply the rays with reduced alpha
        ray_surface.set_alpha(30)
        self.screen.blit(ray_surface, (0, 0))
        
        # Apply screen flash effect on first display
        if not hasattr(self, 'unlock_screen_time'):
            self.unlock_screen_time = current_time
            self.flash_alpha = 255
        
        # Fade out the flash
        if hasattr(self, 'flash_alpha') and self.flash_alpha > 0:
            flash_surf = pygame.Surface((screen_width, screen_height))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(self.flash_alpha)
            self.screen.blit(flash_surf, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 10)
        
        # Draw instructions at bottom
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = "Click on an ability card to unlock it"
        instruction = instruction_font.render(instruction_text, True, (150, 150, 150))
        instruction_pos = ((screen_width - instruction.get_width()) // 2, screen_height - 50)
        self.screen.blit(instruction, instruction_pos)

class Ability:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.unlocked = False


