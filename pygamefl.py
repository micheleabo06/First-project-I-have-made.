import pygame
import random
import sys
import math
import os 

# Removed all custom os.environ['SDL_VIDEODRIVER'] settings.
# Allowing Pygame to use its default, native graphics backend for macOS.

# Initialize Pygame
pygame.init()

#  CONSTANTS (Adjusted for Graphics) 

gridSize = 20 # Original constant name used
TILE_SIZE = 40  # Each grid square will be 40x40 pixels for the display
numberOfEnemies = 5 #
BASE_HEALTH_LOSS = 1
ENEMY_DAMAGE = 8 # damage  

# Screen dimensions based on grid size
# We add 50 pixels at the top for the status bar
SCREEN_WIDTH = gridSize * TILE_SIZE
SCREEN_HEIGHT = gridSize * TILE_SIZE + 50 
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("T O W Grid Adventure")

# Define Colors (RGB tuples)
COLOR_WHITE = (255, 255, 255)
COLOR_GRID = (50, 50, 50)
COLOR_PLAYER = (50, 50, 255)    # Blue for Player (T)
COLOR_GOAL = (0, 150, 0)     # Green for Goal (O)
COLOR_ENEMY = (200, 0, 0)    # Red for Enemy (W)
COLOR_STATUS_BAR = (30, 30, 30)

# Load Font
FONT_STATUS = pygame.font.Font(None, 30)

# VARIABLES 
playerHealth = 100
playerPositionX = 0  # Row index
playerPositionY = 0  # Column index
goalPosition = []
enemyPositions = []
game_over = False

# CORE FUNCTIONS 

def generate_initial_positions():
    global goalPosition, enemyPositions, playerPositionX, playerPositionY
    
    # 1. Ensure Player starts at 0, 0
    playerPositionX = 0
    playerPositionY = 0
    
    # 2. Generate Goal position
    # this also includes 0 right? Yes, randint(0, N) is inclusive.
    goalPosition = [random.randint(0, gridSize - 1), random.randint(0, gridSize - 1)]
    while goalPosition == [playerPositionX, playerPositionY]:
        goalPosition = [random.randint(0, gridSize - 1), random.randint(0, gridSize - 1)]

    # 3. Generate Enemy positions and making up grid
    enemyPositions = []
    while len(enemyPositions) < numberOfEnemies:
        for i in range(numberOfEnemies - len(enemyPositions)):
            x = random.randint(0, gridSize - 1) # starting x
            y = random.randint(0, gridSize - 1) # starting y
            new_pos = [x, y]
            
            # i keep getting confused with != so remember what it means (Not Equal To)
            if (new_pos != goalPosition and 
                new_pos != [playerPositionX, playerPositionY] and 
                new_pos not in enemyPositions):
                enemyPositions.append(new_pos)

def draw_grid():
    # Draw white background for the grid area
    SCREEN.fill(COLOR_WHITE, (0, 50, SCREEN_WIDTH, SCREEN_HEIGHT - 50))
    
    # Draw grid lines
    for i in range(gridSize):
        pygame.draw.line(SCREEN, COLOR_GRID, (i * TILE_SIZE, 50), (i * TILE_SIZE, SCREEN_HEIGHT - 50), 1)
        pygame.draw.line(SCREEN, COLOR_GRID, (0, i * TILE_SIZE + 50), (SCREEN_WIDTH, i * TILE_SIZE + 50), 1)

def draw_elements():
    
    
    # Font for drawing letters (T, O, W)
    font_char = pygame.font.Font(None, int(TILE_SIZE * 0.75))
    
    # Helper to draw centered text on a tile
    # Display the grid - if you dont put reset everything will be that colour so careful (Pygame handles color resets automatically)
    def draw_char_on_tile(char, color, row, col):
        text_surface = font_char.render(char, True, color)
        # Calculate center position of the tile
        center_x = col * TILE_SIZE + TILE_SIZE // 2
        center_y = row * TILE_SIZE + 50 + TILE_SIZE // 2
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        SCREEN.blit(text_surface, text_rect)

    # 1. Draw Goal (O)
    draw_char_on_tile("O", COLOR_GOAL, goalPosition[0], goalPosition[1])
    
    # 2. Draw Enemies (W)
    for x, y in enemyPositions:
        draw_char_on_tile("W", COLOR_ENEMY, x, y)
        
    # 3. Draw Player (T) - Drawn last to be on top
    draw_char_on_tile("T", COLOR_PLAYER, playerPositionX, playerPositionY)

def draw_status_bar(username):
   # Draws the top status bar for health and instructions."""
    SCREEN.fill(COLOR_STATUS_BAR, (0, 0, SCREEN_WIDTH, 50))
    
    # Health Display
    health_text = FONT_STATUS.render(f"Player: {username} | Health: {max(0, playerHealth)} ❤", True, COLOR_WHITE)
    SCREEN.blit(health_text, (10, 15))
    
    # Instructions
    inst_text = FONT_STATUS.render("Move: W/A/S/D | Quit: Q", True, (200, 200, 200))
    SCREEN.blit(inst_text, (SCREEN_WIDTH - inst_text.get_width() - 10, 15))

def final_message(text, color):
    # Displays the end-of-game message centered on the screen."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200) 
    overlay.fill((0, 0, 0)) 
    SCREEN.blit(overlay, (0, 0))
    
    font_final = pygame.font.Font(None, 74)
    text_surface = font_final.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    SCREEN.blit(text_surface, text_rect)
    pygame.display.flip()
    
    # Block execution until game exit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()

def check_game_state(username):
    # check for win or loss condition
    global playerHealth, game_over, enemyPositions
    
    # Check for Enemy Collision (Damage & Removal)
    if [playerPositionX, playerPositionY] in enemyPositions:
        print("You bumped into an enemy :(, -8 health.") # Keep print for terminal feedback
        playerHealth -= ENEMY_DAMAGE
        enemyPositions.remove([playerPositionX, playerPositionY])
        
    # Check for Win
    if [playerPositionX, playerPositionY] == goalPosition:
        draw_status_bar(username) 
        print("You did it! You won! I knew you could do it!") # Keep print for terminal feedback
        final_message(f"You did it, {username}! You won!", COLOR_GOAL)
        game_over = True
        return

    # Check for Death
    if playerHealth <= 0:
        playerHealth = 0
        draw_status_bar(username)
        print("You died :(") # Keep print for terminal feedback
        final_message(f"Game Over, {username}. You died :(", COLOR_ENEMY)
        game_over = True
        return

def direction_to_move(dx, dy, username):
    # Calculates the new position, moves player, and checks state.
    global playerPositionX, playerPositionY, playerHealth
    
    new_x = playerPositionX + dx
    new_y = playerPositionY + dy

    # Check bounds (so you cant go out of bunds)
    if 0 <= new_x < gridSize and 0 <= new_y < gridSize:
        # movement logic - A and D were swapped in old code, Pygame keys handle directions correctly
        playerPositionX = new_x
        playerPositionY = new_y
        
        # Deduct basic movement cost
        playerHealth -= BASE_HEALTH_LOSS 
        
        check_game_state(username) # Check state immediately after move


# MAIN GAME LOOP

def main_game_loop(username):
    global game_over
    
    generate_initial_positions()
    clock = pygame.time.Clock()

    # game loop - took me a while again to find out that i had to use [] and not ()
    while not game_over:
        
        # --- 1. INPUT/EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                
            # Instantaneous key presses for smooth movement
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_w:
                    dx = -1 # Up (W)
                elif event.key == pygame.K_s:
                    dx = 1  # Down (S)
                elif event.key == pygame.K_a:
                    dy = -1 # Left (A)
                elif event.key == pygame.K_d:
                    dy = 1  # Right (D)
                elif event.key == pygame.K_q:
                    game_over = True
                    print("Scaredy Cat") # Keep print for terminal feedback

                if dx != 0 or dy != 0:
                    direction_to_move(dx, dy, username)

        # DRAWING PHASE 
        draw_grid()
        draw_elements()
        draw_status_bar(username)
        
        # UPDATE SCREEN 
        pygame.display.flip()
        
        # Limits the game speed
        clock.tick(30) 

    # Exit pygame cleanly
    if game_over:
        pygame.quit()
        sys.exit()

#  STARTUP LOGIC 

# username making - game starting                      
username = ""
while len(username) < 3:
    username = input("Hi! enter a username: ")
    if len (username) < 3:
        print ("Username too short!")

print(f"Welcome, {username}! Starting graphical game...")
# The game window opens here
main_game_loop(username)

