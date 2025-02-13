import pygame
import json
import os
import time

class StartupScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 32)  # Smaller font size (was 36)
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        
        self.game_description = [
            "Welcome to Matrix Jump",
            "Top Hackers:"
        ]
        
        # Calculate total height needed and starting Y position
        self.line_height = 30  # Reduced line height (was 40)
        total_height = len(self.game_description) * self.line_height
        self.start_y = self.height * 0.15  # Start at 15% from the top (was height - total_height / 2)
        
        self.highscores = self.load_highscores()
        
    def load_highscores(self):
        try:
            with open('highscores.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
            
    def save_highscore(self, name, score):
        if name in self.highscores:
            if score > self.highscores[name]:
                self.highscores[name] = score
        else:
            self.highscores[name] = score
            
        with open('highscores.json', 'w') as f:
            json.dump(self.highscores, f)
            
    def get_player_highscore(self, name):
        return self.highscores.get(name, 0)
        
    def get_top_scores(self, limit=3):
        # Sort scores in descending order and get top N
        sorted_scores = sorted(self.highscores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:limit]
        
    def draw_text_lines(self, completed_lines, current_line="", current_line_index=0):
        self.screen.fill(self.BLACK)
        
        # Draw all completed lines
        for i, line in enumerate(completed_lines):
            text_surface = self.font.render(line, True, self.GREEN)
            y_pos = self.start_y + (i * self.line_height)
            x_pos = (self.width - text_surface.get_width()) // 2  # Center horizontally
            self.screen.blit(text_surface, (x_pos, y_pos))
            
            # If this is the "Top Hackers:" line and it's completed
            if line == "Top Hackers:":
                self.draw_high_scores(y_pos + self.line_height)
            
        # Draw current typing line
        if current_line:
            text_surface = self.font.render(current_line, True, self.GREEN)
            y_pos = self.start_y + (current_line_index * self.line_height)
            x_pos = (self.width - text_surface.get_width()) // 2  # Center horizontally
            self.screen.blit(text_surface, (x_pos, y_pos))
            
            # If we're typing the "Top Hackers:" line
            if current_line_index == len(self.game_description) - 1:
                self.draw_high_scores(y_pos + self.line_height)
            
        pygame.display.flip()
        
    def draw_high_scores(self, y_position):
        top_scores = self.get_top_scores()
        
        if not top_scores:
            text = "No scores yet..."
            text_surface = self.font.render(text, True, self.GREEN)
            x_pos = (self.width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (x_pos, y_position))
        else:
            for i, (name, score) in enumerate(top_scores):
                text = f"{i+1}. {name}: {score}"
                text_surface = self.font.render(text, True, self.GREEN)
                x_pos = (self.width - text_surface.get_width()) // 2
                self.screen.blit(text_surface, (x_pos, y_position + i * self.line_height))
        
    def type_text(self):
        completed_lines = []
        
        for i, line in enumerate(self.game_description):
            current_text = ""
            for char in line:
                current_text += char
                self.draw_text_lines(completed_lines, current_text, i)
                time.sleep(0.05)
                
                # Check for quit event
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:  # Skip animation
                            current_text = line
                            break
            
            completed_lines.append(line)
            
        # Make sure final screen is drawn completely
        self.draw_text_lines(completed_lines)
        return True
        
    def get_player_name(self):
        name_prompt = "Enter your name to begin..."
        prompt_y = self.start_y + (len(self.game_description) + 7) * self.line_height  # After high scores
        
        input_box = pygame.Rect(0, 0, self.width//3, 40)
        input_box.centerx = self.width // 2
        input_box.top = prompt_y + self.line_height
        
        name = ""
        done = False
        clock = pygame.time.Clock()
        cursor_visible = True
        cursor_timer = 0
        background = pygame.Surface((self.width, self.height))
        
        # Draw the static background once
        background.fill(self.BLACK)
        self.draw_text_lines(self.game_description)
        self.draw_high_scores(self.start_y + len(self.game_description) * self.line_height)
        prompt_surface = self.font.render(name_prompt, True, self.GREEN)
        prompt_rect = prompt_surface.get_rect(center=(self.width//2, prompt_y))
        background.blit(prompt_surface, prompt_rect)
        
        while not done:
            clock.tick(60)  # Limit FPS to reduce flickering
            cursor_timer += 1
            if cursor_timer >= 30:  # Toggle cursor every 30 frames
                cursor_timer = 0
                cursor_visible = not cursor_visible
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key != pygame.K_RETURN:  # Allow any key except return
                        if len(name) < 15 and event.unicode.isprintable():
                            name += event.unicode
            
            # Draw the static background
            self.screen.blit(background, (0, 0))
            
            # Draw input box and text
            pygame.draw.rect(self.screen, self.GREEN, input_box, 2)
            text_surface = self.font.render(name + ('|' if cursor_visible else ''), True, self.GREEN)
            text_rect = text_surface.get_rect(center=input_box.center)
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            
        return name.strip()
        
    def show(self):
        if self.type_text() is None:
            return None
            
        # Create static background without input elements
        background = pygame.Surface((self.width, self.height))
        background.fill(self.BLACK)
        
        # Draw the description and high scores
        self.draw_text_lines(self.game_description)
        
        # Create a copy of the screen state for background
        background.blit(self.screen, (0, 0))
        
        # Get player name
        return self.get_player_name(background)
        
    def get_player_name(self, background):
        # Calculate positions relative to the last high score entry
        top_scores = self.get_top_scores(5)  # Get top 5 scores
        scores_height = len(top_scores) * self.line_height if top_scores else self.line_height
        
        # Position prompt after the scores with some padding
        name_prompt = "Enter your name to begin..."
        prompt_y = (self.start_y + 
                   (len(self.game_description) * self.line_height) +  # Height of description
                   scores_height +  # Height of scores
                   self.line_height * 2)  # Extra padding
        
        # Position input box below prompt
        input_box = pygame.Rect(0, 0, self.width//3, 40)
        input_box.centerx = self.width // 2
        input_box.top = prompt_y + self.line_height
        
        name = ""
        done = False
        clock = pygame.time.Clock()
        cursor_visible = True
        cursor_timer = 0
        
        while not done:
            clock.tick(60)
            cursor_timer += 1
            if cursor_timer >= 30:
                cursor_timer = 0
                cursor_visible = not cursor_visible
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key != pygame.K_RETURN:
                        if len(name) < 15 and event.unicode.isprintable():
                            name += event.unicode
            
            # Draw everything
            self.screen.blit(background, (0, 0))
            
            # Draw semi-transparent overlay
            overlay_height = self.line_height * 4
            overlay = pygame.Surface((self.width, overlay_height))
            overlay.fill(self.BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, prompt_y - self.line_height))
            
            # Draw prompt text
            prompt_surface = self.font.render(name_prompt, True, self.GREEN)
            prompt_rect = prompt_surface.get_rect(center=(self.width//2, prompt_y))
            self.screen.blit(prompt_surface, prompt_rect)
            
            # Draw input box with background
            pygame.draw.rect(self.screen, self.BLACK, input_box.inflate(4, 4))
            pygame.draw.rect(self.screen, self.GREEN, input_box, 2)
            
            # Draw input text with cursor
            display_text = name + ('|' if cursor_visible else ' ')
            text_surface = self.font.render(display_text, True, self.GREEN)
            text_rect = text_surface.get_rect(center=input_box.center)
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            
        return name.strip()