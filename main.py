import pygame
import random
import sys
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT * BLOCK_SIZE) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GLASS_COLOR = (255, 255, 255, 128)
BUTTON_COLOR = (60, 60, 80)
BUTTON_HOVER_COLOR = (80, 80, 100)
TEXT_COLOR = (200, 200, 200)

# Tetromino shapes and colors
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (0, 255, 0),    # Green
    (255, 0, 0)     # Red
]

def create_gradient_background(width, height):
    surface = pygame.Surface((width, height))
    top_color = (40, 40, 60)
    bottom_color = (20, 20, 30)
    
    for y in range(height):
        factor = y / height
        color = tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(top_color, bottom_color))
        pygame.draw.line(surface, color, (0, y), (width, y))
    
    return surface

class Button:
    def __init__(self, x, y, width, height, text, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Tetris")
        
        # Create background
        self.background = create_gradient_background(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Create UI elements
        self.font = pygame.font.Font(None, 36)
        self.new_game_button = Button(50, 120, 200, 50, "New Game")
        
        self.grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_piece = self.new_piece()
        self.clock = pygame.time.Clock()

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (50, 50))

    def new_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }

    def draw_block(self, x, y, color):
        rect = pygame.Rect(
            GRID_OFFSET_X + x * BLOCK_SIZE,
            GRID_OFFSET_Y + y * BLOCK_SIZE,
            BLOCK_SIZE - 1,
            BLOCK_SIZE - 1
        )
        
        # Create glass effect
        s = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 180), s.get_rect())
        pygame.draw.rect(s, (*WHITE, 50), (0, 0, BLOCK_SIZE//2, BLOCK_SIZE//2))
        self.screen.blit(s, rect)

    def draw_grid(self):
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw grid background with glass effect
        s = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 255, 255, 30), s.get_rect())
        self.screen.blit(s, (GRID_OFFSET_X, GRID_OFFSET_Y))
        
        # Draw grid lines
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (GRID_OFFSET_X + x * BLOCK_SIZE, GRID_OFFSET_Y),
                (GRID_OFFSET_X + x * BLOCK_SIZE, GRID_OFFSET_Y + GRID_HEIGHT * BLOCK_SIZE)
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                (100, 100, 100),
                (GRID_OFFSET_X, GRID_OFFSET_Y + y * BLOCK_SIZE),
                (GRID_OFFSET_X + GRID_WIDTH * BLOCK_SIZE, GRID_OFFSET_Y + y * BLOCK_SIZE)
            )

        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    self.draw_block(x, y, self.grid[y][x])

        # Draw current piece
        if not self.game_over:
            for y, row in enumerate(self.current_piece['shape']):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_block(
                            self.current_piece['x'] + x,
                            self.current_piece['y'] + y,
                            self.current_piece['color']
                        )

        # Draw UI elements
        self.draw_score()
        self.new_game_button.draw(self.screen)

        if self.game_over:
            game_over_text = self.font.render("Game Over!", True, TEXT_COLOR)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)

    def move(self, dx, dy):
        if self.game_over:
            return False
            
        self.current_piece['x'] += dx
        self.current_piece['y'] += dy
        
        if not self.is_valid_position():
            self.current_piece['x'] -= dx
            self.current_piece['y'] -= dy
            if dy > 0:  # If moving down, place the piece
                self.place_piece()
                self.clear_lines()
                self.current_piece = self.new_piece()
                if not self.is_valid_position():
                    self.game_over = True
            return False
        return True

    def rotate(self):
        if self.game_over:
            return
            
        old_shape = self.current_piece['shape']
        self.current_piece['shape'] = list(zip(*reversed(self.current_piece['shape'])))
        if not self.is_valid_position():
            self.current_piece['shape'] = old_shape

    def is_valid_position(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pos_x = self.current_piece['x'] + x
                    pos_y = self.current_piece['y'] + y
                    if (pos_x < 0 or pos_x >= GRID_WIDTH or
                        pos_y < 0 or pos_y >= GRID_HEIGHT or
                        self.grid[pos_y][pos_x]):
                        return False
        return True

    def place_piece(self):
        for y, row in enumerate(self.current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']

    def clear_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                lines_cleared += 1
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2 - 1][:]
                self.grid[0] = [None] * GRID_WIDTH
            else:
                y -= 1
        
        self.score += lines_cleared * 100

    def run(self):
        fall_time = 0
        fall_speed = 500  # milliseconds
        
        while True:
            time_delta = self.clock.tick(60)/1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_LEFT:
                            self.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            self.move(0, 1)
                        elif event.key == pygame.K_UP:
                            self.rotate()
                        elif event.key == pygame.K_SPACE:
                            while self.move(0, 1):
                                pass
                
                if self.new_game_button.handle_event(event):
                    self.__init__()
            
            fall_time += self.clock.get_rawtime()
            if fall_time >= fall_speed and not self.game_over:
                self.move(0, 1)
                fall_time = 0
            
            self.draw_grid()
            pygame.display.flip()

if __name__ == "__main__":
    game = Tetris()
    game.run()