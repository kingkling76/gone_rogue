# player.py
import pygame
import random
import math
from platforms import StartPlatform  # Add this import


class Player(pygame.sprite.Sprite):
    def __init__(self, walk_sprite_sheet, idle_sprite_sheet, punch_sprite_sheet):
        super().__init__()
        
        # Load sprite sheets
        self.walk_frames = self.load_frames(walk_sprite_sheet, 10)
        self.idle_frames = self.load_frames(idle_sprite_sheet, 6)
        self.punch_frames = self.load_frames(punch_sprite_sheet, 4)
        
        # Initialize sprite state
        self.current_frame = 0
        self.image = self.idle_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(400, 550))
        
        # Movement parameters
        self.vel_x = 5
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_strength = 12
        self.on_ground = False
        self.moving = False
        self.facing_right = True
        
        # Animation parameters
        self.punching = False
        self.animation_timer = 0
        self.animation_delay = 5
        
        # Teleport parameters
        self.is_teleporting = False
        self.teleport_pos = None
        self.teleport_speed = 10
        self.teleport_move_speed = 5
        self.teleport_progress = 0
        self.teleport_distortions = pygame.sprite.Group()
        
        # Special abilities
        self.time_slow_active = False
        self.time_slow_factor = 0.3
        self.time_slow_duration = 5000
        self.time_slow_start = 0
        
        self.matrix_vision_active = False
        self.matrix_vision_duration = 8000
        self.matrix_vision_start = 0
        
        self.wall_running = False
        self.wall_run_timer = 0
        self.wall_run_duration = 2000
        
        self.shield_active = False
        self.shield_health = 100
        self.shield_regen_rate = 0.5
        
        self.last_burst_time = 0
        self.burst_cooldown = 3000
        
        self.dash_distance = 200
        self.dash_cooldown = 1000
        self.last_dash_time = 0
        
        self.controlled_enemy = None
        self.control_duration = 5000
        self.control_start_time = 0
        
        # Special effects groups
        self.teleport_effects = pygame.sprite.Group()
        
        # Doppelganger
        self.doppelganger = None
        self.all_sprites = None

        self.on_platform = False


    def load_frames(self, sprite_sheet, num_frames):
        frames = []
        frame_width = sprite_sheet.get_width() // num_frames
        frame_height = sprite_sheet.get_height()
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frames.append(frame)
        return frames

    def update(self):
        if self.is_teleporting:
            self.teleport()
        elif self.punching:
            self.animate_punch()
        else:
            self.normal_update()
            
        # Update effects
        self.teleport_effects.update()
        self.teleport_distortions.update()
        if self.doppelganger:
            self.doppelganger.update()

    def normal_update(self):
        keys = pygame.key.get_pressed()
        self.moving = False

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.vel_x
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.vel_x
            self.moving = True
            self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_platform:
            self.vel_y = -self.jump_strength
            self.on_platform = False

        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800

        # Animations
        if self.moving:
            self.animate_walk()
        else:
            self.animate_idle()

    def animate_walk(self):
        self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        frame = self.walk_frames[self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def animate_idle(self):
        self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
        frame = self.idle_frames[self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def animate_punch(self):
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.current_frame += 1
            if self.current_frame >= len(self.punch_frames):
                self.current_frame = 0
                self.punching = False
            self.animation_timer = 0
        
        frame = self.punch_frames[self.current_frame]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def punch(self):
        self.punching = True
        self.current_frame = 0
        self.animation_timer = 0

    def trigger_teleport(self, destination):
        if not self.punching:
            self.teleport_pos = destination
            self.is_teleporting = True
            for _ in range(5):
                distortion = TeleportDistortion(self.rect.centerx, self.rect.centery)
                self.teleport_distortions.add(distortion)

    def teleport(self):
        if self.teleport_pos:
            self.rect.center = self.teleport_pos
            self.is_teleporting = False
            self.teleport_pos = None
            self.teleport_distortions.update()

    def create_doppelganger(self):
        if not self.doppelganger and self.all_sprites is not None:
            self.doppelganger = Doppelganger(self.walk_frames)
            self.doppelganger.rect.center = (self.rect.centerx + 100, self.rect.centery)
            self.all_sprites.add(self.doppelganger)

    def activate_time_slow(self):
        if not self.time_slow_active:
            self.time_slow_active = True
            self.time_slow_start = pygame.time.get_ticks()
            for sprite in self.all_sprites:
                if sprite != self:
                    sprite.vel_x *= self.time_slow_factor
                    sprite.vel_y *= self.time_slow_factor

    def activate_matrix_vision(self):
        self.matrix_vision_active = True
        self.matrix_vision_start = pygame.time.get_ticks()

    def wall_run(self):
        if self.is_near_wall() and not self.wall_running:
            self.wall_running = True
            self.wall_run_timer = pygame.time.get_ticks()
            self.gravity = 0

    def activate_shield(self):
        if not self.shield_active:
            self.shield_active = True
            self.shield_health = 100
            shield_surface = self.create_shield_effect()
            self.image.blit(shield_surface, (0, 0))

    def create_shield_effect(self):
        shield_radius = 40
        shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, (0, 255, 0, 128), (shield_radius, shield_radius), shield_radius)
        return shield_surface

    def code_burst(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_burst_time >= self.burst_cooldown:
            self.last_burst_time = current_time
            for effect in range(8):  # Create 8 burst particles
                angle = effect * (360 / 8)
                dx = math.cos(math.radians(angle)) * 5
                dy = math.sin(math.radians(angle)) * 5
                particle = TeleportEffect(self.rect.centerx, self.rect.centery)
                particle.vel_x = dx
                particle.vel_y = dy
                self.teleport_effects.add(particle)

    def digital_dash(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= self.dash_cooldown:
            self.last_dash_time = current_time
            target_x = self.rect.x + (self.dash_distance if self.facing_right else -self.dash_distance)
            for _ in range(5):  # Create dash effect particles
                effect = TeleportEffect(self.rect.centerx, self.rect.centery)
                self.teleport_effects.add(effect)
            self.rect.x = target_x

    def system_hack(self, target_enemy):
        if not self.controlled_enemy:
            self.controlled_enemy = target_enemy
            self.control_start_time = pygame.time.get_ticks()
            target_enemy.image.fill((0, 255, 0))  # Change color to indicate control

    def is_near_wall(self):
        # Simple wall detection - can be improved based on your game's needs
        return self.rect.left <= 0 or self.rect.right >= 800
    
    def handle_platform_collision(self, platforms):
        """Handle collision with platforms"""
        self.on_platform = False
        for platform in platforms:
            if (self.rect.bottom >= platform.rect.top and 
                self.rect.bottom <= platform.rect.bottom and 
                self.rect.right >= platform.rect.left and 
                self.rect.left <= platform.rect.right and 
                self.vel_y >= 0):
                
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_platform = True
                
                # Move with platform
                self.rect.x += platform.speed
                
                # Handle starting platform
                if isinstance(platform, StartPlatform) and not platform.has_jumped:
                    platform.has_jumped = True
                    platform.kill()  # Remove the platform


class TeleportEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect(center=(x, y))
        self.life_time = random.randint(5, 10)
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.scale = random.uniform(0.5, 1.5)
        
        self.color = pygame.Color(random.randint(0, 255), 
                                random.randint(0, 255), 
                                random.randint(0, 255))
        self.image.fill(self.color)
        self.image = pygame.transform.scale(self.image, 
                                          (int(20 * self.scale), int(20 * self.scale)))

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life_time -= 1
        self.image.set_alpha(max(0, int(self.life_time * 12)))
        if self.life_time <= 0:
            self.kill()

class TeleportDistortion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (25, 25), 25, 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.scale = 1.0
        self.alpha = 255
        self.max_scale = 3
        self.life_time = 20

    def update(self):
        self.scale += 0.1
        self.alpha -= 12
        if self.scale >= self.max_scale or self.alpha <= 0:
            self.kill()

        self.image = pygame.Surface((50 * self.scale, 50 * self.scale), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), 
                         (25 * self.scale, 25 * self.scale), 
                         25 * self.scale, 3)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.rect.center)

class Doppelganger(pygame.sprite.Sprite):
    def __init__(self, walk_frames):
        super().__init__()
        self.frames = walk_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(400, 550))
        
        # Movement parameters
        self.vel_x = 5
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_strength = 12
        self.on_ground = False
        self.moving = False
        self.facing_right = True
        
        # Animation
        self.animation_speed = 0.2
        self.animation_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.moving = False
        
        if keys[pygame.K_a]:
            self.rect.x -= self.vel_x
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_d]:
            self.rect.x += self.vel_x
            self.moving = True
            self.facing_right = True
        if keys[pygame.K_w] and self.on_ground:
            self.vel_y = -self.jump_strength
            self.on_ground = False
        
        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        # Ground collision
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.vel_y = 0
            self.on_ground = True
        
        # Screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800
        
        if self.moving:
            self.animate()

    def animate(self):
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0
            
            frame = self.frames[self.current_frame]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

class Fireball(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, image):
        super().__init__()
        self.original_image = image
        self.image = pygame.transform.scale(self.original_image, (20, 20))
        self.rect = self.image.get_rect(center=start_pos)

        # Calculate direction and angle
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle = math.degrees(math.atan2(-dy, dx))  # Negative dy for correct angle
        
        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Calculate normalized direction vector
        distance = math.hypot(dx, dy)
        self.direction = (dx / distance, dy / distance)
        self.speed = 10

    def update(self):
        # Move the fireball
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed