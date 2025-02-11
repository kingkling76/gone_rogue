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
        
        # Create raindrop columns
        self.columns = [random.randint(-height, 0) for _ in range(width // font_size)]
    
    def draw(self, screen):
        for i in range(len(self.columns)):
            x = i * self.font_size
            y = self.columns[i]
            text = self.font.render(str(random.choice([0, 1])), True, GREEN)
            screen.blit(text, (x, y))
            self.columns[i] += self.speed
            
            # Reset column when reaching bottom
            if self.columns[i] > self.height:
                self.columns[i] = random.randint(-50, 0)
