import pygame

import pygame
import random


import pygame
import random

class TeleportEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))  # Initially green, can change later
        self.image.set_alpha(128)  # Make it semi-transparent
        self.rect = self.image.get_rect(center=(x, y))
        self.life_time = random.randint(5, 10)  # Varying lifespan of particles
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.scale = random.uniform(0.5, 1.5)  # Random particle size

        # Randomly change color to create a glowing effect
        self.color = pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.image.fill(self.color)
        self.image = pygame.transform.scale(self.image, (int(20 * self.scale), int(20 * self.scale)))

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.life_time -= 1
        self.image.set_alpha(max(0, int(self.life_time * 12)))  # Fade out over time
        if self.life_time <= 0:
            self.kill()  # Remove particle when life time is up

class TeleportDistortion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (25, 25), 25, 3)  # Green circle with transparency
        self.rect = self.image.get_rect(center=(x, y))
        self.scale = 1.0
        self.alpha = 255
        self.max_scale = 3  # The maximum scale of the ring
        self.life_time = 20  # How long the ring will last

    def update(self):
        # Increase the scale to make the ring expand
        self.scale += 0.1
        self.alpha -= 12  # Fade out the ring over time
        if self.scale >= self.max_scale or self.alpha <= 0:
            self.kill()  # Remove the distortion effect when it finishes

        # Scale and apply the alpha transparency
        self.image = pygame.Surface((50 * self.scale, 50 * self.scale), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 0), (25 * self.scale, 25 * self.scale), 25 * self.scale, 3)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.rect.center)

class Doppelganger(pygame.sprite.Sprite):
    def __init__(self, walk_frames):
        super().__init__()
        
        # Initialize the doppelganger with pre-loaded frames
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
        
        # Animation parameters
        self.animation_speed = 0.2
        self.animation_timer = 0

    def update(self):
        """Update movement and animation for doppelganger"""
        keys = pygame.key.get_pressed()  # WASD controls for doppelganger
        
        self.moving = False
        
        if keys[pygame.K_a]:  # Move left with 'A'
            self.rect.x -= self.vel_x
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_d]:  # Move right with 'D'
            self.rect.x += self.vel_x
            self.moving = True
            self.facing_right = True
        if keys[pygame.K_w] and self.on_ground:  # Jump with 'W'
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
        
        # Keep doppelganger within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800
        
        # Animate if moving
        if self.moving:
            self.animate()

    def animate(self):
        """Cycle through the walk frames"""
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.animation_timer = 0
            
            # Get the frame and flip if facing left
            frame = self.frames[self.current_frame]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

class Player(pygame.sprite.Sprite):
    def __init__(self, walk_sprite_sheet, idle_sprite_sheet, punch_sprite_sheet):
        super().__init__()

        # Load sprite sheets
        self.walk_frames = self.load_frames(walk_sprite_sheet, 10)
        self.idle_frames = self.load_frames(idle_sprite_sheet, 6)
        self.punch_frames = self.load_frames(punch_sprite_sheet, 4)

        self.current_frame = 0
        self.image = self.idle_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(400, 550))

        # Movement and animation parameters
        self.vel_x = 5
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_strength = 12
        self.on_ground = False
        self.moving = False
        self.facing_right = True
        self.punching = False  # Initialize the punching state
        self.animation_timer = 0
        self.animation_delay = 5  # Delay between frames for the punch animation

        # Teleport parameters
        self.is_teleporting = False
        self.teleport_pos = None
        self.teleport_speed = 10  # Slower teleport speed
        self.teleport_move_speed = 5  # Speed of moving toward the teleport position
        self.teleport_progress = 0  # Keeps track of teleport progress
        self.teleport_distortions = pygame.sprite.Group()


        self.time_slow_active = False
        self.time_slow_factor = 0.3
        self.time_slow_duration = 5000  # 5 seconds
        self.time_slow_start = 0
        
        self.matrix_vision_active = False
        self.matrix_vision_duration = 8000  # 8 seconds
        self.matrix_vision_start = 0
        
        self.wall_running = False
        self.wall_run_timer = 0
        self.wall_run_duration = 2000  # 2 seconds
        
        self.shield_active = False
        self.shield_health = 100
        self.shield_regen_rate = 0.5
        
        self.last_burst_time = 0
        self.burst_cooldown = 3000  # 3 seconds
        
        self.dash_distance = 200
        self.dash_cooldown = 1000  # 1 second
        self.last_dash_time = 0
        
        self.controlled_enemy = None
        self.control_duration = 5000  # 5 seconds
        self.control_start_time = 0

        # Teleport effect group
        self.teleport_effects = pygame.sprite.Group()

        self.doppelganger = None
    def activate_time_slow(self):
        if not self.time_slow_active:
            self.time_slow_active = True
            self.time_slow_start = pygame.time.get_ticks()
            # Apply slow motion effect to all relevant game objects
            for sprite in self.all_sprites:
                if sprite != self:
                    sprite.velocity_x *= self.time_slow_factor
                    sprite.velocity_y *= self.time_slow_factor

    def activate_matrix_vision(self):
        """Reveals hidden paths, enemies, and interactive objects"""
        self.matrix_vision_active = True
        self.matrix_vision_start = pygame.time.get_ticks()
        # Create matrix rain effect that reveals secrets
        self.create_matrix_vision_effect()

    def wall_run(self):
        """Allows running on vertical surfaces"""
        if self.is_near_wall() and not self.wall_running:
            self.wall_running = True
            self.wall_run_timer = pygame.time.get_ticks()
            self.gravity = 0
            # Add wall running particles
            self.create_wall_run_particles()

    def activate_shield(self):
        """Creates a protective data shield"""
        if not self.shield_active:
            self.shield_active = True
            self.shield_health = 100
            # Create shield visual effect
            self.create_shield_effect()

    def code_burst(self):
        """Creates an omnidirectional energy wave"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_burst_time >= self.burst_cooldown:
            self.last_burst_time = current_time
            # Create expanding ring effect
            self.create_burst_effect()
            # Damage and push back nearby enemies
            self.apply_burst_damage()

    def digital_dash(self):
        """Quick teleport dash in facing direction"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time >= self.dash_cooldown:
            self.last_dash_time = current_time
            # Calculate dash endpoint
            target_x = self.rect.x + (self.dash_distance if self.facing_right else -self.dash_distance)
            # Create dash effect
            self.create_dash_effect(target_x)
            # Move player
            self.rect.x = target_x

    def system_hack(self, target_enemy):
        """Take control of an enemy"""
        if not self.controlled_enemy:
            self.controlled_enemy = target_enemy
            self.control_start_time = pygame.time.get_ticks()
            # Apply control effect
            self.apply_control_effect(target_enemy)

    def recursive_clone(self):
        """Create a clone that can also create clones"""
        if self.doppelganger:
            clone_position = (
                self.doppelganger.rect.centerx + 50,
                self.doppelganger.rect.centery
            )
            new_clone = Doppelganger(self.walk_frames)
            new_clone.rect.center = clone_position
            self.all_sprites.add(new_clone)
            # Create clone spawn effect
            self.create_clone_effect(clone_position)


    def create_shield_effect(self):
        shield_radius = 40
        shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, (0, 255, 0, 128), (shield_radius, shield_radius), shield_radius)
        return shield_surface


    def create_doppelganger(self):
            """Create a doppelganger controlled by WASD keys"""
            if not self.doppelganger and self.all_sprites is not None:
                print("Creating doppelganger...")  # Debug print
                self.doppelganger = Doppelganger(self.walk_frames)
                self.doppelganger.rect.center = (self.rect.centerx + 100, self.rect.centery)
                self.all_sprites.add(self.doppelganger)
                print("Doppelganger added to sprites")  # Debug print

    def load_frames(self, sprite_sheet, num_frames):
        frames = []
        frame_width = sprite_sheet.get_width() // num_frames
        for i in range(num_frames):
            frame = sprite_sheet.subsurface(i * frame_width, 0, frame_width, sprite_sheet.get_height())
            frames.append(frame)
        return frames

    def update(self):
        if self.is_teleporting:
            self.teleport()
        elif self.punching:
            self.animate_punch()  # Call the punch animation when punching
        else:
            self.normal_update()
        if self.doppelganger:
            self.doppelganger.update()

        # Update teleport effects
        self.teleport_effects.update()

    def normal_update(self):
        keys = pygame.key.get_pressed()
        self.moving = False  # Reset moving state

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.vel_x
            self.moving = True
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.vel_x
            self.moving = True
            self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_strength
            self.on_ground = False

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.vel_y = 0
            self.on_ground = True

        # Normal animation updates
        if self.moving:
            self.animate_walk()
        else:
            self.animate_idle()

    def animate_punch(self):
        """Cycle through the punch frames with a delay"""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_delay:
            self.current_frame += 1
            if self.current_frame >= len(self.punch_frames):
                self.current_frame = 0
                self.punching = False  # Reset punching once the animation is finished
            self.animation_timer = 0  # Reset timer
        
        # Flip the punch frames if facing left
        if self.facing_right:
            self.image = self.punch_frames[self.current_frame]
        else:
            self.image = pygame.transform.flip(self.punch_frames[self.current_frame], True, False)

    def animate_walk(self):
        # Walking animation logic
        self.current_frame += 1
        if self.current_frame >= len(self.walk_frames):
            self.current_frame = 0
        self.image = self.walk_frames[self.current_frame]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def animate_idle(self):
        # Idle animation logic
        self.current_frame += 1
        if self.current_frame >= len(self.idle_frames):
            self.current_frame = 0
        self.image = self.idle_frames[self.current_frame]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def trigger_teleport(self, destination):
            if not self.punching:  # Only trigger teleport when not punching
                # Set teleport destination and trigger the effect
                self.teleport_pos = destination
                self.is_teleporting = True

                # Create teleport distortion effects (rings)
                for _ in range(5):  # More rings for a more dramatic effect
                    distortion = TeleportDistortion(self.rect.centerx, self.rect.centery)
                    self.teleport_distortions.add(distortion)

    def teleport(self):
        """Teleport player to the new position instantly with distortion rings"""
        if self.teleport_pos:
            self.rect.center = self.teleport_pos
            self.is_teleporting = False  # Teleportation complete
            self.teleport_pos = None  # Clear teleport position

            # Add distortions to the screen
            self.teleport_distortions.update()

    def punch(self):
        """Start the punch animation"""
        self.punching = True
        self.current_frame = 0  # Reset punch animation frame
        self.animation_timer = 0  # Reset animation timer


import math

import pygame
import math

class Fireball(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, image):
        super().__init__()

        self.original_image = image  # Keep the original image for later rotations
        self.image = pygame.transform.scale(self.original_image, (20, 20))  # Scale the fireball down
        self.rect = self.image.get_rect(center=start_pos)

        # Calculate the direction vector to move the fireball
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        
        # Normalize the vector to have a magnitude of 1 and multiply by speed
        self.direction = (dx / distance, dy / distance)
        self.speed = 10  # Speed of the fireball

        # Calculate the angle for rotation
        angle = math.degrees(math.atan2(dy, dx))
        self.image = pygame.transform.rotate(self.image, -angle)  # Rotate the image
        self.rect = self.image.get_rect(center=self.rect.center)  # Adjust the rect to match rotated image

    def update(self):
        # Move the fireball in the direction of the mouse click
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Remove fireball if it goes off screen
        if self.rect.right < 0 or self.rect.left > 800 or self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()
