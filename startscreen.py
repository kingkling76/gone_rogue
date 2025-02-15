import pygame
import json
import os
import time

import pygame
import json
import os
import time

class StartupScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 32)
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        self.HOVER_GREEN = (0, 200, 0)
        
        self.menu_options = ["Play", "About", "Quit"]
        self.selected_option = None
        
        self.game_description = [
            "Welcome to Matrix Jump",
            "Top Hackers:"
        ]
        
        self.intro_sequences = [
            ["A game by", "Your Name Here"],
            ["In the year 2099", "The digital realm became reality"],
            ["Mega-corporations control the data streams", "Power flows through their networks"],
            ["But in the shadows...", "A lone hacker rises"],
            ["Armed with nothing but skill", "You must breach their systems"],
            ["Jump through the Matrix", "Collect the forbidden data"],
            ["Survive...", "And become legend"]
        ]
        
        self.line_height = 30
        self.start_y = self.height * 0.15
        
        self.highscores = self.load_highscores()

    def fade_text(self, lines, fade_in_time=2.0, display_time=2.0, fade_out_time=2.0):
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 48)  # Larger font for intro text
        
        # Calculate total frames for each phase
        fade_in_frames = int(fade_in_time * 60)
        display_frames = int(display_time * 60)
        fade_out_frames = int(fade_out_time * 60)
        
        # Fade in
        for i in range(fade_in_frames + 1):
            alpha = int((i / fade_in_frames) * 255)
            self.screen.fill(self.BLACK)
            
            for j, line in enumerate(lines):
                text_surface = font.render(line, True, self.GREEN)
                text_surface.set_alpha(alpha)
                text_rect = text_surface.get_rect(center=(self.width//2, self.height//2 - len(lines)*20 + j*50))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return True
        
        # Full display
        for _ in range(display_frames):
            self.screen.fill(self.BLACK)
            
            for j, line in enumerate(lines):
                text_surface = font.render(line, True, self.GREEN)
                text_rect = text_surface.get_rect(center=(self.width//2, self.height//2 - len(lines)*20 + j*50))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return True
        
        # Fade out
        for i in range(fade_out_frames + 1):
            alpha = 255 - int((i / fade_out_frames) * 255)
            self.screen.fill(self.BLACK)
            
            for j, line in enumerate(lines):
                text_surface = font.render(line, True, self.GREEN)
                text_surface.set_alpha(alpha)
                text_rect = text_surface.get_rect(center=(self.width//2, self.height//2 - len(lines)*20 + j*50))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return True
        
        return True

    def play_intro(self):
        # Add a "Press any key to skip" message
        skip_font = pygame.font.Font(None, 24)
        skip_text = skip_font.render("Press SPACE or ENTER to skip", True, self.GREEN)
        skip_rect = skip_text.get_rect(bottom=self.height - 20, centerx=self.width//2)
        
        for sequence in self.intro_sequences:
            # Draw skip message
            self.screen.fill(self.BLACK)
            self.screen.blit(skip_text, skip_rect)
            pygame.display.flip()
            
            result = self.fade_text(sequence)
            if result is None:  # If the user quits, stop
                return None
            elif result is False:  # If skipped, break out
                break

        # Ensure the last frame is visible before switching to the menu
        pygame.time.delay(1000)  # Add a 1-second pause before menu
        
        return True


    def show(self):
        # Play intro sequence first
        if self.play_intro() is None:
            return None
            
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.screen.fill(self.BLACK)
            
            # Draw title
            title_surface = self.font.render("Matrix Jump", True, self.GREEN)
            title_rect = title_surface.get_rect(center=(self.width//2, self.height * 0.2))
            self.screen.blit(title_surface, title_rect)
            
            # Draw menu
            self.draw_menu()
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        result = self.handle_menu_click()
                        if result == "quit":
                            return None
                        elif result is not None:
                            return result
            
            clock.tick(60)
    
    def draw_menu(self):
        menu_start_y = self.height * 0.4
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.menu_options):
            option_rect = pygame.Rect(0, 0, 200, 40)
            option_rect.centerx = self.width // 2
            option_rect.centery = menu_start_y + (i * 60)
            
            # Check if mouse is hovering over option
            color = self.HOVER_GREEN if option_rect.collidepoint(mouse_pos) else self.GREEN
            
            # Draw the option
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=option_rect.center)
            
            # Draw a rectangle around the option
            pygame.draw.rect(self.screen, color, option_rect, 2)
            self.screen.blit(text_surface, text_rect)
            
            # Update selected option based on mouse position
            if option_rect.collidepoint(mouse_pos):
                self.selected_option = i
    
    def handle_menu_click(self):
        if self.selected_option is not None:
            if self.menu_options[self.selected_option] == "Play":
                return self.start_game()
            elif self.menu_options[self.selected_option] == "About":
                return self.show_about()
            elif self.menu_options[self.selected_option] == "Quit":
                return "quit"
        return None
    
    def show_about(self):
        about_text = [
            "Matrix Jump",
            "A cyberpunk platformer game",
            "Navigate through the digital realm",
            "collecting data fragments and avoiding",
            "security systems.",
            "",
            "Press ESC to return to menu"
        ]
        
        done = False
        while not done:
            self.screen.fill(self.BLACK)
            
            for i, line in enumerate(about_text):
                text_surface = self.font.render(line, True, self.GREEN)
                text_rect = text_surface.get_rect(center=(self.width//2, self.start_y + i * self.line_height))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        done = True
                        
        return self.show()
    
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
        sorted_scores = sorted(self.highscores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:limit]
    
    def draw_text_lines(self, completed_lines, current_line="", current_line_index=0):
        self.screen.fill(self.BLACK)
        
        for i, line in enumerate(completed_lines):
            text_surface = self.font.render(line, True, self.GREEN)
            y_pos = self.start_y + (i * self.line_height)
            x_pos = (self.width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (x_pos, y_pos))
            
            if line == "Top Hackers:":
                self.draw_high_scores(y_pos + self.line_height)
        
        if current_line:
            text_surface = self.font.render(current_line, True, self.GREEN)
            y_pos = self.start_y + (current_line_index * self.line_height)
            x_pos = (self.width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (x_pos, y_pos))
            
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
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            current_text = line
                            break
            
            completed_lines.append(line)
        
        self.draw_text_lines(completed_lines)
        return True
    
    def start_game(self):
        if self.type_text() is None:
            return None
            
        background = pygame.Surface((self.width, self.height))
        background.fill(self.BLACK)
        self.draw_text_lines(self.game_description)
        background.blit(self.screen, (0, 0))
        
        return self.get_player_name(background)
    
    def show(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.screen.fill(self.BLACK)
            
            # Draw title
            title_surface = self.font.render("Matrix Jump", True, self.GREEN)
            title_rect = title_surface.get_rect(center=(self.width//2, self.height * 0.2))
            self.screen.blit(title_surface, title_rect)
            
            # Draw menu
            self.draw_menu()
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        result = self.handle_menu_click()
                        if result == "quit":
                            return None
                        elif result is not None:
                            return result
            
            clock.tick(60)
    
    def get_player_name(self, background):
        top_scores = self.get_top_scores(5)
        scores_height = len(top_scores) * self.line_height if top_scores else self.line_height
        
        name_prompt = "Enter your name to begin..."
        prompt_y = (self.start_y + 
                   (len(self.game_description) * self.line_height) +
                   scores_height +
                   self.line_height * 2)
        
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
            
            self.screen.blit(background, (0, 0))
            
            overlay_height = self.line_height * 4
            overlay = pygame.Surface((self.width, overlay_height))
            overlay.fill(self.BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, prompt_y - self.line_height))
            
            prompt_surface = self.font.render(name_prompt, True, self.GREEN)
            prompt_rect = prompt_surface.get_rect(center=(self.width//2, prompt_y))
            self.screen.blit(prompt_surface, prompt_rect)
            
            pygame.draw.rect(self.screen, self.BLACK, input_box.inflate(4, 4))
            pygame.draw.rect(self.screen, self.GREEN, input_box, 2)
            
            display_text = name + ('|' if cursor_visible else ' ')
            text_surface = self.font.render(display_text, True, self.GREEN)
            text_rect = text_surface.get_rect(center=input_box.center)
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            
        return name.strip()