import pygame
import random

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

class MatrixRain:
    def __init__(self, width, height, font_size=20, speed=5):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.speed = speed
        self.font = pygame.font.Font(None, font_size)
        
        # Create raindrop rows instead of columns
        self.rows = [random.randint(-width, 0) for _ in range(height // font_size)]
    
    def draw(self, screen):
        for i in range(len(self.rows)):
            y = i * self.font_size
            x = self.rows[i]
            text = self.font.render(str(random.choice([0, 1])), True, GREEN)
            screen.blit(text, (x, y))
            self.rows[i] += self.speed
            
            # Reset row when reaching right edge
            if self.rows[i] > self.width:
                self.rows[i] = random.randint(-50, 0)