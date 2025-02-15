import pygame
import pygame
import random
import math

class PauseMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.width, self.height = screen.get_size()
        self.options = ["Resume", "Restart", "Quit"]
        self.selected = 0
        self.alpha = 0
        self.active = False
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.time = 0
        
        # Matrix rain effect
        self.matrix_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        self.rain_drops = [(random.randint(0, self.width), random.randint(0, self.height)) 
                          for _ in range(50)]
        
        # Glowing effect parameters
        self.glow_strength = 0
        self.glow_direction = 1
        
        # Digital glitch effect
        self.glitch_lines = []
        self.glitch_timer = 0
        
        # Hexagonal menu border points
        self.hex_points = self._calculate_hex_points()

    def _calculate_hex_points(self):
        # Calculate points for hexagonal shape
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(self.width, self.height) // 3
        points = []
        for i in range(6):
            angle = math.pi / 3 * i + math.pi / 6
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        return points

    def toggle(self):
        self.active = not self.active
        self.alpha = 0 if self.active else 255
        if self.active:
            self.glitch_lines = self._generate_glitch_lines()

    def _generate_glitch_lines(self):
        lines = []
        for _ in range(random.randint(3, 7)):
            y = random.randint(0, self.height)
            width = random.randint(20, 100)
            offset = random.randint(-10, 10)
            lines.append((y, width, offset))
        return lines

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self._generate_glitch_lines()  # Add glitch effect on selection change
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self._generate_glitch_lines()  # Add glitch effect on selection change
            elif event.key == pygame.K_RETURN:
                if self.options[self.selected] == "Resume":
                    return "Resume"
                elif self.options[self.selected] == "Restart":
                    return "Restart"
                elif self.options[self.selected] == "Quit":
                    return "Quit"
        return None

    def _draw_matrix_rain(self):
        for i, (x, y) in enumerate(self.rain_drops):
            # Draw Matrix character
            char = random.choice(self.matrix_chars)
            color = (0, random.randint(150, 255), 0, random.randint(50, 150))
            text = self.font.render(char, True, color)
            self.overlay.blit(text, (x, y))
            
            # Move drop down
            self.rain_drops[i] = (x, (y + 5) % self.height)
            
            # Random chance to reset position
            if random.random() < 0.02:
                self.rain_drops[i] = (random.randint(0, self.width), 0)

    def _draw_hex_border(self):
        # Draw outer glow
        glow_color = (0, min(255, 100 + self.glow_strength), 0)
        for i in range(3):
            offset = i * 2
            pygame.draw.polygon(self.screen, glow_color, 
                              [(p[0] + offset, p[1] + offset) for p in self.hex_points], 
                              2)
            
        # Draw main border
        pygame.draw.polygon(self.screen, (0, 255, 0), self.hex_points, 2)
        
        # Draw corner accents
        for point in self.hex_points:
            pygame.draw.circle(self.screen, (0, 255, 0), (int(point[0]), int(point[1])), 3)

    def _draw_glitch_effects(self):
        for y, width, offset in self.glitch_lines:
            glitch_rect = pygame.Rect(self.width//2 - width//2 + offset, y, width, 2)
            pygame.draw.rect(self.screen, (0, random.randint(200, 255), 0), glitch_rect)

    def draw(self):
        if not self.active:
            return
        
        self.time += 0.05
        
        # Update glow effect
        self.glow_strength += self.glow_direction * 2
        if self.glow_strength >= 100 or self.glow_strength <= 0:
            self.glow_direction *= -1

        # Clear overlay
        self.overlay.fill((0, 0, 0, 0))
        
        # Draw matrix rain effect
        self._draw_matrix_rain()
        
        # Apply overlay with fade-in
        if self.alpha < 180:
            self.alpha += 10
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill((0, 0, 0, self.alpha))
        self.screen.blit(background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw hexagonal border
        self._draw_hex_border()
        
        # Draw menu title with digital effect
        title = "SYSTEM PAUSED"
        title_color = (0, 255, 0)
        if random.random() < 0.05:  # Occasional glitch effect
            title = "SYST3M P4US3D"
            title_color = (0, 200, 255)
        title_text = self.font.render(title, True, title_color)
        title_pos = (self.width//2 - title_text.get_width()//2, 
                    self.height//2 - 100)
        self.screen.blit(title_text, title_pos)
        
        # Draw menu options with effects
        for i, option in enumerate(self.options):
            # Calculate position with sine wave effect
            base_y = self.height//2 - 20 + i * 50
            offset = math.sin(self.time + i) * 3
            y = base_y + offset
            
            # Determine color based on selection
            if i == self.selected:
                color = (0, 255, 0)
                # Draw selection indicator
                indicator = ">" if int(self.time * 2) % 2 == 0 else ">"
                ind_text = self.font.render(indicator, True, color)
                self.screen.blit(ind_text, (self.width//2 - 100, y))
            else:
                color = (0, 150, 0)
            
            # Draw option text
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(self.width//2, y))
            self.screen.blit(text, text_rect)
            
            # Add scan line effect for selected option
            if i == self.selected:
                scan_pos = int((self.time * 100) % text_rect.height)
                pygame.draw.line(self.screen, (0, 255, 0, 128),
                               (text_rect.left, text_rect.top + scan_pos),
                               (text_rect.right, text_rect.top + scan_pos))
        
        # Draw glitch effects
        self._draw_glitch_effects()
        
        # Occasionally update glitch lines
        self.glitch_timer += 1
        if self.glitch_timer > 30:
            self.glitch_timer = 0
            if random.random() < 0.3:
                self.glitch_lines = self._generate_glitch_lines()

