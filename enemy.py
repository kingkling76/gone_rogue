import pygame
import random
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.enemy_images = [
            'drone.png',
            'virussymbol.png',
        ]
        
        # Animation settings
        self.sprite_sheet = None
        self.animation_frames = []
        self.animation_index = 0
        self.animation_speed = 0.2  # Adjust if animation is too fast/slow
        self.last_update = pygame.time.get_ticks()
        
        try:
            # Load sprite sheet for drone
            self.sprite_sheet = pygame.image.load("assets/walk_scan.png").convert_alpha()
            print(f"Sprite sheet dimensions: {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}")
            
            # Initialize animation frames
            self.setup_animation_frames()
            
            if self.animation_frames:
                self.image = self.animation_frames[0]
                print(f"Successfully loaded {len(self.animation_frames)} animation frames")
            else:
                raise pygame.error("No animation frames were loaded")
                
        except pygame.error as e:
            print(f"Failed to load sprite sheet: {e}")
            # Fallback to regular images
            try:
                chosen_image = random.choice(self.enemy_images)
                self.image = pygame.image.load("assets/" + str(chosen_image)).convert_alpha()
                self.image = pygame.transform.scale(self.image, (50, 50))
            except pygame.error:
                print(f"Enemy image not found. Using default rectangle.")
                self.image = pygame.Surface((60, 60))
                self.image.fill((0, 255, 0))
        
        self.rect = self.image.get_rect().inflate(-60, -60)
        self.speed = 3
        self.spawn_position(screen_width, screen_height)
        self.vel_x, self.vel_y = self.calculate_velocity(screen_width, screen_height)
        

    def setup_animation_frames(self):
        try:
            sheet_width = self.sprite_sheet.get_width()
            sheet_height = self.sprite_sheet.get_height()
            
            # Try to detect if frames are arranged horizontally
            frame_width = sheet_width // 8  # Assuming 8 frames in a row
            frame_height = sheet_height
            
            # If the above doesn't look right, try a 4x2 grid arrangement
            if frame_width < frame_height:
                frame_width = sheet_width // 4
                frame_height = sheet_height // 2
            
            print(f"Detected frame size: {frame_width}x{frame_height}")
            
            # Clear any existing frames
            self.animation_frames = []
            
            # For horizontal arrangement (8x1)
            if sheet_height == frame_height:
                for col in range(8):
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(self.sprite_sheet, (0, 0), 
                             (col * frame_width, 0, frame_width, frame_height))
                    frame = pygame.transform.scale(frame, (50, 50))
                    self.animation_frames.append(frame)
            # For grid arrangement (4x2)
            else:
                for row in range(2):
                    for col in range(4):
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(self.sprite_sheet, (0, 0), 
                                 (col * frame_width, row * frame_height, 
                                  frame_width, frame_height))
                        frame = pygame.transform.scale(frame, (50, 50))
                        self.animation_frames.append(frame)
            
            print(f"Extracted {len(self.animation_frames)} frames")
            
        except Exception as e:
            print(f"Error in setup_animation_frames: {str(e)}")
            raise pygame.error("Failed to setup animation frames")

    def animate(self):
        if not self.animation_frames:
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.animation_index = (self.animation_index + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.animation_index]

    def spawn_position(self, screen_width, screen_height):
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
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        dx = center_x - self.rect.centerx
        dy = center_y - self.rect.centery
        
        distance = max(1, (dx * dx + dy * dy) ** 0.5)
        dx = dx / distance * self.speed
        dy = dy / distance * self.speed
        
        return dx, dy

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        if self.animation_frames:
            self.animate()