import pygame
import random
import os

class Platform(pygame.sprite.Sprite):
    def __init__(self, screen_width):
        super().__init__()
        # Load and scale the platform image
        try:
            # Try to load the platform image
            self.image = pygame.image.load("gone_rogue\\assets\\server.png").convert_alpha()
            # Scale the image to desired size
            self.image = pygame.transform.scale(self.image, (100, 20))  # Adjust size as needed
        except pygame.error:
            # Fallback to rectangle if image loading fails
            print("Platform image not found. Using default rectangle.")
            self.image = pygame.Surface((100, 20))
            self.image.fill((255, 255, 255))
            
        self.rect = self.image.get_rect()
        
        # Randomly choose starting side
        self.direction = random.choice([-1, 1])  # -1 for left to right, 1 for right to left
        
        # Set initial position
        if self.direction == -1:  # Start from left
            self.rect.x = -self.rect.width
            self.speed = 2  # Move right
        else:  # Start from right
            self.rect.x = screen_width
            self.speed = -2  # Move left
            
        # Random vertical position between top and bottom of screen
        self.rect.y = random.randint(100, 500)
        
    def update(self):
        # Move horizontally
        self.rect.x += self.speed