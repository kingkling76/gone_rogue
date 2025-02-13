import pygame
import random
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        # List of possible enemy image filenames
        self.enemy_images = [
            'drone.png',
            'virussymbol.png',
        ]
        
        try:
            # Randomly choose one of the enemy images
            chosen_image = random.choice(self.enemy_images)
            self.image = pygame.image.load("assets/" + str(chosen_image)).convert_alpha()
            # Scale the image to desired size
            self.image = pygame.transform.scale(self.image, (50, 50))  # Adjust size as needed
        except pygame.error:
            # Fallback to rectangle if image loading fails
            print(f"Enemy image not found. Using default rectangle.")
            self.image = pygame.Surface((60, 60))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect()
        
        # Randomly choose a starting position from any edge
        self.spawn_position(screen_width, screen_height)
        
        # Set speed based on spawn position
        self.speed = 3
        self.vel_x, self.vel_y = self.calculate_velocity(screen_width, screen_height)

    def spawn_position(self, screen_width, screen_height):
        # Choose a random side (0: top, 1: right, 2: bottom, 3: left)
        side = random.randint(0, 3)
        
        if side == 0:  # Top
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = -self.rect.height
        elif side == 1:  # Right
            self.rect.x = screen_width
            self.rect.y = random.randint(0, screen_height - self.rect.height)
        elif side == 2:  # Bottom
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = screen_height
        else:  # Left
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, screen_height - self.rect.height)

    def calculate_velocity(self, screen_width, screen_height):
        # Calculate direction towards center of screen
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Calculate direction vector
        dx = center_x - self.rect.centerx
        dy = center_y - self.rect.centery
        
        # Normalize the direction vector
        distance = max(1, (dx * dx + dy * dy) ** 0.5)
        dx = dx / distance * self.speed
        dy = dy / distance * self.speed
        
        return dx, dy

    def update(self):
        # Move enemy
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y