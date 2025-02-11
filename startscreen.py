import pygame
import sys
import main  # Import the main game file

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Matrix Jump - Start Screen")

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Font settings
font = pygame.font.Font(None, 50)

def startscreen():
    screen.fill(BLACK)
    
    # Render title
    title_text = font.render("Matrix Jump", True, GREEN)
    start_text = font.render("Press any key to start", True, WHITE)

    # Position text at the center
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    screen.blit(title_text, title_rect)
    screen.blit(start_text, start_rect)

    pygame.display.flip()

    # Wait for key press to start the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:  # Any key starts the game
                waiting = False

    pygame.quit()
    main.run_game()  # Run the main game after exiting the start screen

if __name__ == "__main__":
    startscreen()
