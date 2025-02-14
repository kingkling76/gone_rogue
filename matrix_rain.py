import pygame
import random

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

import pygame
import random

class MatrixRain:
    def __init__(self, width, height, font_size=20, speed=5):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.speed = speed
        
        # Try to load a more Matrix-like font, fall back to default if not available
        try:
            self.font = pygame.font.Font("MS Mincho.ttf", font_size)
        except:
            self.font = pygame.font.Font(None, font_size)
        
        # Matrix characters (Japanese katakana and other symbols)
        self.matrix_chars = [chr(int('0x30a0', 16) + i) for i in range(96)]
        self.matrix_chars.extend(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                                ':', '>', '<', '=', '?', '*', '$', '#', '@'])
        
        # Create multiple layers of rain for depth effect
        self.rain_layers = []
        
        # First layer (brightest, fastest)
        self.rain_layers.append({
            'drops': self.create_drops(),
            'speed': speed,
            'color': (0, 255, 0),  # Bright green
            'alpha': 255
        })
        
        # Second layer (medium brightness, medium speed)
        self.rain_layers.append({
            'drops': self.create_drops(),
            'speed': speed * 0.8,
            'color': (0, 200, 0),  # Medium green
            'alpha': 200
        })
        
        # Third layer (darkest, slowest)
        self.rain_layers.append({
            'drops': self.create_drops(),
            'speed': speed * 0.6,
            'color': (0, 150, 0),  # Dark green
            'alpha': 150
        })
        
        # Create bright leading characters
        self.leading_drops = self.create_drops()
        
        # Initialize fade effect for each column
        self.fade_lengths = [random.randint(5, 20) for _ in range(width // font_size)]

    def create_drops(self):
        """Create initial raindrops with random positions and lengths"""
        drops = []
        for x in range(0, self.width, self.font_size):
            drops.append({
                'x': x,
                'y': random.randint(-self.height, 0),
                'length': random.randint(5, 30),
                'chars': [random.choice(self.matrix_chars) for _ in range(30)],
                'change_timer': 0
            })
        return drops

    def update_drops(self, drops, speed):
        """Update raindrop positions and characters"""
        for drop in drops:
            # Update position
            drop['y'] += speed
            
            # Reset drop when it goes off screen
            if drop['y'] > self.height:
                drop['y'] = random.randint(-self.height, 0)
                drop['length'] = random.randint(5, 30)
            
            # Occasionally change characters
            drop['change_timer'] += 1
            if drop['change_timer'] >= 5:  # Change every 5 frames
                drop['change_timer'] = 0
                # Randomly change some characters in the stream
                for i in range(len(drop['chars'])):
                    if random.random() < 0.1:  # 10% chance to change each character
                        drop['chars'][i] = random.choice(self.matrix_chars)

    def draw(self, screen):
        # Create a surface for the rain with alpha channel
        rain_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw each layer of rain
        for layer in self.rain_layers:
            self.update_drops(layer['drops'], layer['speed'])
            
            for drop in layer['drops']:
                # Draw the stream of characters
                for i in range(drop['length']):
                    y_pos = int(drop['y']) - i * self.font_size
                    if 0 <= y_pos < self.height:
                        # Calculate fade effect
                        fade = 1 - (i / drop['length'])
                        char_alpha = int(layer['alpha'] * fade)
                        char_color = (*layer['color'], char_alpha)
                        
                        # Render character
                        char_surface = self.font.render(drop['chars'][i], True, char_color)
                        rain_surface.blit(char_surface, (drop['x'], y_pos))
        
        # Draw bright leading characters
        self.update_drops(self.leading_drops, self.speed * 1.2)
        for drop in self.leading_drops:
            if 0 <= drop['y'] < self.height:
                # Bright white-green leading character
                lead_char = self.font.render(drop['chars'][0], True, (180, 255, 180))
                rain_surface.blit(lead_char, (drop['x'], int(drop['y'])))
        
        # Add occasional bright flashes
        if random.random() < 0.05:  # 5% chance each frame
            flash_x = random.randint(0, self.width - self.font_size)
            flash_y = random.randint(0, self.height - self.font_size)
            flash_char = self.font.render(random.choice(self.matrix_chars), True, (255, 255, 255))
            rain_surface.blit(flash_char, (flash_x, flash_y))
        
        # Draw the final rain surface to the screen
        screen.blit(rain_surface, (0, 0))