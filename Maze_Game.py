import pygame
import random
import heapq
import math
import sys
from pygame import gfxdraw

class MazeGame:
    def __init__(self):
        # Game constants
        self.WIDTH, self.HEIGHT = 603, 804
        self.ROWS, self.COLS = 20, 20
        self.CELL_SIZE = 30
        self.MAZE_OFFSET_Y = 200
        
        # Colors
        self.COLORS = {
            'WHITE': (255, 255, 255),
            'BLACK': (0, 0, 0),
            'RED': (255, 50, 50),
            'BLUE': (50, 150, 255),
            'GREEN': (50, 255, 50),
            'YELLOW': (255, 255, 50),
            'PURPLE': (180, 50, 220),
            'DARK_GRAY': (40, 40, 50),
            'LIGHT_GRAY': (220, 220, 230),
            'Background': (170,170,170),
            'Wall': (31,56,100),
            'ORANGE': (255, 165, 0)
        }
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Interactive Maze Game")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Game state
        self.reset_game()
        
        # UI Elements
        self.create_ui_elements()
        
    def reset_game(self):
        self.maze = self.generate_maze()
        self.start = (0, 0)
        self.goal = (self.COLS-1, self.ROWS-1)
        self.player = self.start
        self.ai_position = self.start
        self.ai_path = self.a_star(self.ai_position, self.goal)
        self.ai_previous_positions = []
        
        # Dijkstra AI initialization
        self.dijkstra_position = self.start
        self.dijkstra_path = self.dijkstra(self.dijkstra_position, self.goal)
        self.dijkstra_previous_positions = []
        
        # Trail tracking
        self.ai_trail = []
        self.dijkstra_trail = []
        
        self.game_over = False
        self.victory = False
        self.particles = []
        self.confetti = [self.Confetti() for _ in range(150)]
        self.celebration_alpha = 0
        self.celebration_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        
        # Animation states
        self.player_anim = 0
        self.player_target = self.player
        self.player_prev = self.player
        
        self.ai_anim = 0
        self.ai_target = self.ai_position
        self.ai_prev = self.ai_position
        
        self.dijkstra_anim = 0
        self.dijkstra_target = self.dijkstra_position
        self.dijkstra_prev = self.dijkstra_position
        
        # Auto AI
        self.auto_ai = False
        self.auto_ai_timer = 0
        
        # Auto Dijkstra
        self.auto_dijkstra = False
        self.auto_dijkstra_timer = 0
        
        # Help screen
        self.show_help = False
    
    def create_ui_elements(self):
        # Create buttons with base color, hover color, and click color
        self.move_ai_button = self.Button(20, 20, 140, 40, "Move A* AI", 
                                        (100, 255, 100), (50, 220, 50), (30, 180, 30))
        self.undo_ai_button = self.Button(170, 20, 140, 40, "Undo A* AI", 
                                        (255, 255, 100), (220, 220, 50), (180, 180, 30))
        self.auto_ai_button = self.Button(320, 20, 140, 40, "Auto A* AI", 
                                        (180, 100, 255), (150, 50, 220), (120, 30, 180))
        self.reset_button = self.Button(470, 20, 120, 40, "Reset Game",  
                                    (255, 100, 100), (220, 50, 50), (180, 30, 30))
        self.move_dijkstra_button = self.Button(20, 70, 140, 40, "Move Dijkstra AI", 
                                            (255, 200, 100), (220, 170, 50), (180, 140, 30))
        self.undo_dijkstra_button = self.Button(170, 70, 140, 40, "Undo Dijkstra AI", 
                                            (255, 180, 50), (220, 150, 30), (180, 120, 20))
        self.auto_dijkstra_button = self.Button(320, 70, 140, 40, "Auto Dijkstra AI", 
                                            (255, 150, 50), (220, 120, 30), (180, 90, 20))
        self.help_button = self.Button(470, 70, 80, 40, "Help", 
                                    (100, 100, 255), (50, 50, 220), (30, 30, 180))
        
        # Create sliders
        self.speed_slider = self.Slider(20, 140, 200, 20, 1, 20, 10, "Speed")
        self.maze_size_slider = self.Slider(240, 140, 200, 20, 10, 30, self.ROWS, "Maze Size")

    class Button:
        def __init__(self, x, y, width, height, text, color, hover_color, click_color, rounded=True):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.hover_color = hover_color
            self.click_color = click_color
            self.current_color = color
            self.rounded = rounded
            self.pressed = False
            self.hover_anim = 0
            self.click_anim = 0
            self.shadow_offset = 3
            self.shadow_color = (0, 0, 0, 100)
            
        def draw(self, surface, font):
            # Create text surface
            text_surf = font.render(self.text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            
            # Click animation - button press effect
            if self.click_anim > 0:
                offset = math.sin(self.click_anim * 0.2) * 3
                draw_rect = self.rect.move(0, offset)
                current_shadow_offset = max(1, self.shadow_offset - 2)  # Reduce shadow when pressed
                self.click_anim -= 1
            else:
                draw_rect = self.rect
                current_shadow_offset = self.shadow_offset
            
            # Draw shadow
            shadow_rect = draw_rect.move(current_shadow_offset, current_shadow_offset)
            if self.rounded:
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, self.shadow_color, 
                            (0, 0, shadow_rect.width, shadow_rect.height), 
                            border_radius=5)
                surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
            
            # Hover effect - matches button size exactly
            if self.hover_anim > 0:
                hover_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                alpha = min(100, self.hover_anim * 5)  # Max alpha of 100
                if self.rounded:
                    pygame.draw.rect(hover_surf, (*self.hover_color[:3], alpha), 
                                (0, 0, self.rect.width, self.rect.height), 
                                border_radius=5)
                else:
                    pygame.draw.rect(hover_surf, (*self.hover_color[:3], alpha), 
                                (0, 0, self.rect.width, self.rect.height))
                surface.blit(hover_surf, (self.rect.x, self.rect.y))
            
            # Main button
            if self.rounded:
                pygame.draw.rect(surface, self.current_color, draw_rect, border_radius=5)
                pygame.draw.rect(surface, (0, 0, 0), draw_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(surface, self.current_color, draw_rect)
                pygame.draw.rect(surface, (0, 0, 0), draw_rect, 2)
            
            # Adjust text position when pressed
            if self.pressed:
                text_rect.y += 2
            
            surface.blit(text_surf, text_rect)
            
        def check_hover(self, pos):
            if self.rect.collidepoint(pos):
                self.current_color = self.hover_color
                if self.hover_anim < 20:  # 20 frames to reach full hover effect
                    self.hover_anim += 4
                return True
            else:
                self.current_color = self.color
                if self.hover_anim > 0:
                    self.hover_anim -= 4
                return False
        
        def is_clicked(self, pos, event):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(pos):
                    self.pressed = True
                    self.click_anim = 10
                    self.current_color = self.click_color
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pressed:
                    self.pressed = False
                    self.current_color = self.hover_color if self.rect.collidepoint(pos) else self.color
                    return False
            return False

    class Slider:
        def __init__(self, x, y, width, height, min_val, max_val, initial_val, text):
            self.rect = pygame.Rect(x, y, width, height)
            self.min = min_val
            self.max = max_val
            self.value = initial_val
            self.dragging = False
            self.text = text
            self.knob_rect = pygame.Rect(x, y, 20, height + 10)
            self.update_knob()
            
        def update_knob(self):
            normalized_value = (self.value - self.min) / (self.max - self.min)
            self.knob_rect.centerx = self.rect.x + normalized_value * self.rect.width
            
        def draw(self, surface, font):
            # Track
            pygame.draw.rect(surface, (220, 220, 230), self.rect, border_radius=5)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=5)
            
            # Filled portion
            fill_width = (self.value - self.min) / (self.max - self.min) * self.rect.width
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, (50, 150, 255), fill_rect, border_radius=5)
            
            # Knob
            pygame.draw.rect(surface, (255, 255, 255), self.knob_rect, border_radius=5)
            pygame.draw.rect(surface, (0, 0, 0), self.knob_rect, 2, border_radius=5)
            
            # Text
            text_surf = font.render(f"{self.text}: {int(self.value)}", True, (0, 0, 0))
            surface.blit(text_surf, (self.rect.x, self.rect.y - 20))
            
        def handle_event(self, event):
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.knob_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                    self.dragging = True
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                relative_x = mouse_pos[0] - self.rect.x
                normalized_value = max(0, min(1, relative_x / self.rect.width))
                self.value = self.min + normalized_value * (self.max - self.min)
                self.update_knob()
                return True
            return False

    class Particle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.size = random.randint(3, 8)
            self.color = random.choice([
                (255, 50, 50), (50, 255, 50), (50, 150, 255), 
                (255, 255, 50), (255, 50, 255), (50, 255, 255), 
                (255, 180, 50)
            ])
            self.speed = random.uniform(2, 6)
            self.angle = random.uniform(0, math.pi * 2)
            self.lifetime = random.randint(40, 80)
            self.alpha = 255
            self.gravity = random.uniform(0.05, 0.2)
        
        def update(self):
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed + self.gravity
            self.lifetime -= 1
            self.alpha = max(0, self.alpha - 3)
            self.speed *= 0.98
        
        def draw(self, surface):
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.size, self.size), self.size)
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

    class Confetti:
        def __init__(self):
            self.reset()
            
        def reset(self):
            self.x = random.randint(0, 900)
            self.y = random.randint(-100, -10)
            self.size = random.randint(5, 15)
            self.color = random.choice([
                (255, 50, 50), (50, 255, 50), (50, 150, 255), 
                (255, 255, 50), (255, 50, 255), (50, 255, 255), 
                (255, 180, 50)
            ])
            self.speed = random.uniform(2, 5)
            self.angle = random.uniform(-0.1, 0.1)
            self.rotation = 0
            self.rot_speed = random.uniform(-5, 5)
            self.shape = random.choice(["rect", "circle", "triangle"])
            self.wobble = random.uniform(0, math.pi*2)
            self.wobble_speed = random.uniform(0.05, 0.2)
        
        def update(self):
            self.y += self.speed
            self.x += self.angle * 2 + math.sin(self.wobble) * 1.5
            self.rotation += self.rot_speed
            self.wobble += self.wobble_speed
            
            if self.y > 800 + 20:
                self.reset()
        
        def draw(self, surface):
            if self.shape == "rect":
                s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.rect(s, self.color, (0, 0, self.size, self.size))
                s = pygame.transform.rotate(s, self.rotation)
                surface.blit(s, (int(self.x - self.size//2), int(self.y - self.size//2)))
            elif self.shape == "circle":
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size//2)
            else:
                points = [
                    (self.x, self.y - self.size//2),
                    (self.x - self.size//2, self.y + self.size//2),
                    (self.x + self.size//2, self.y + self.size//2)
                ]
                rotated_points = []
                for px, py in points:
                    px -= self.x
                    py -= self.y
                    new_x = px * math.cos(math.radians(self.rotation)) - py * math.sin(math.radians(self.rotation))
                    new_y = px * math.sin(math.radians(self.rotation)) + py * math.cos(math.radians(self.rotation))
                    rotated_points.append((new_x + self.x, new_y + self.y))
                pygame.draw.polygon(surface, self.color, rotated_points)

    def generate_maze(self):
        maze = [[1 for _ in range(self.COLS)] for _ in range(self.ROWS)]
        start_x, start_y = 0, 0
        maze[start_y][start_x] = 0

        walls = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = start_x + dx, start_y + dy
            if 0 <= nx < self.COLS and 0 <= ny < self.ROWS:
                walls.append((nx, ny, start_x, start_y))

        while walls:
            wall_index = random.randint(0, len(walls)-1)
            wx, wy, cx, cy = walls.pop(wall_index)
            nx, ny = cx + (wx - cx)*2, cy + (wy - cy)*2
            if 0 <= nx < self.COLS and 0 <= ny < self.ROWS:
                if maze[ny][nx] == 1:
                    maze[wy][wx] = 0
                    maze[ny][nx] = 0
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_wx, new_wy = nx + dx, ny + dy
                        if 0 <= new_wx < self.COLS and 0 <= new_wy < self.ROWS and maze[new_wy][new_wx] == 1:
                            walls.append((new_wx, new_wy, nx, ny))
            else:
                maze[wy][wx] = 0

        maze[0][0] = 0
        maze[self.ROWS-1][self.COLS-1] = 0
        return maze

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star(self, start, end):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < self.COLS and 0 <= neighbor[1] < self.ROWS and self.maze[neighbor[1]][neighbor[0]] == 0:
                    temp_g_score = g_score[current] + 1
                    if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = temp_g_score
                        f_score[neighbor] = temp_g_score + self.heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def dijkstra(self, start, end):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        cost_so_far = {start: 0}
        
        while open_set:
            current_cost, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < self.COLS and 0 <= neighbor[1] < self.ROWS and self.maze[neighbor[1]][neighbor[0]] == 0:
                    new_cost = cost_so_far[current] + 1
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        came_from[neighbor] = current
                        heapq.heappush(open_set, (new_cost, neighbor))
        return []

    def draw_maze(self):
        for y in range(self.ROWS):
            for x in range(self.COLS):
                color = self.COLORS['Background'] if self.maze[y][x] == 0 else self.COLORS['Wall']
                pygame.draw.rect(self.screen, color, 
                                (x * self.CELL_SIZE, y * self.CELL_SIZE + self.MAZE_OFFSET_Y, 
                                 self.CELL_SIZE, self.CELL_SIZE))

    def draw_trails(self):
        # Draw A* trail (yellow)
        for i, (x, y) in enumerate(self.ai_trail):
            alpha = min(255, 150 + i * 3)  # Fade effect for older positions
            s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.COLORS['YELLOW'], alpha//2), 
                            (0, 0, self.CELL_SIZE, self.CELL_SIZE), border_radius=2)
            self.screen.blit(s, (x * self.CELL_SIZE, y * self.CELL_SIZE + self.MAZE_OFFSET_Y))
        
        # Draw Dijkstra trail (orange)
        for i, (x, y) in enumerate(self.dijkstra_trail):
            alpha = min(255, 150 + i * 3)  # Fade effect for older positions
            s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.COLORS['ORANGE'], alpha//2), 
                            (0, 0, self.CELL_SIZE, self.CELL_SIZE), border_radius=2)
            self.screen.blit(s, (x * self.CELL_SIZE, y * self.CELL_SIZE + self.MAZE_OFFSET_Y))

    def draw_path(self):
        if self.ai_path:
            for i, (x, y) in enumerate(self.ai_path[:0]):
                alpha = 255 - i * 50
                if alpha <= 0:
                    break
                s = pygame.Surface((self.CELL_SIZE//2, self.CELL_SIZE//2), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.COLORS['PURPLE'], alpha), 
                                (0, 0, self.CELL_SIZE//2, self.CELL_SIZE//2))
                self.screen.blit(s, 
                               (x * self.CELL_SIZE + self.CELL_SIZE//4, 
                                y * self.CELL_SIZE + self.MAZE_OFFSET_Y + self.CELL_SIZE//4))

    def create_particles(self, x, y, count=100):
        return [self.Particle(x, y) for _ in range(count)]

    def move_player(self, dx, dy):
        if self.game_over:
            return
            
        new_pos = (self.player[0] + dx, self.player[1] + dy)
        if (0 <= new_pos[0] < self.COLS and 
            0 <= new_pos[1] < self.ROWS and 
            self.maze[new_pos[1]][new_pos[0]] == 0):
            
            self.player_prev = self.player
            self.player_target = new_pos
            self.player_anim = 10
            self.player = new_pos
            
            if new_pos == self.goal:
                self.game_over = True
                self.victory = True
                goal_x = self.goal[0] * self.CELL_SIZE + self.CELL_SIZE // 2
                goal_y = self.goal[1] * self.CELL_SIZE + self.MAZE_OFFSET_Y + self.CELL_SIZE // 2
                self.particles = self.create_particles(goal_x, goal_y, 200)

    def move_ai(self):
        if self.game_over or not self.ai_path:
            return
            
        # Add current position to trail before moving
        self.ai_trail.append(self.ai_position)
        
        self.ai_previous_positions.append(self.ai_position)
        if len(self.ai_previous_positions) > 100:
            self.ai_previous_positions.pop(0)
            
        self.ai_prev = self.ai_position
        self.ai_position = self.ai_path.pop(0)
        self.ai_target = self.ai_position
        self.ai_anim = 10
        
        if not self.ai_path:
            self.ai_path = self.a_star(self.ai_position, self.goal)

    def move_dijkstra(self):
        if self.game_over or not self.dijkstra_path:
            return
            
        # Add current position to trail before moving
        self.dijkstra_trail.append(self.dijkstra_position)
        
        self.dijkstra_previous_positions.append(self.dijkstra_position)
        if len(self.dijkstra_previous_positions) > 100:
            self.dijkstra_previous_positions.pop(0)
            
        self.dijkstra_prev = self.dijkstra_position
        self.dijkstra_position = self.dijkstra_path.pop(0)
        self.dijkstra_target = self.dijkstra_position
        self.dijkstra_anim = 10
        
        if not self.dijkstra_path:
            self.dijkstra_path = self.dijkstra(self.dijkstra_position, self.goal)

    def undo_ai_move(self):
        if self.ai_previous_positions:
            # Remove last position from trail
            if self.ai_trail:
                self.ai_trail.pop()
                
            self.ai_prev = self.ai_position
            self.ai_position = self.ai_previous_positions.pop()
            self.ai_target = self.ai_position
            self.ai_anim = 10
            self.ai_path = self.a_star(self.ai_position, self.goal)

    def undo_dijkstra_move(self):
        if self.dijkstra_previous_positions:
            # Remove last position from trail
            if self.dijkstra_trail:
                self.dijkstra_trail.pop()
                
            self.dijkstra_prev = self.dijkstra_position
            self.dijkstra_position = self.dijkstra_previous_positions.pop()
            self.dijkstra_target = self.dijkstra_position
            self.dijkstra_anim = 10
            self.dijkstra_path = self.dijkstra(self.dijkstra_position, self.goal)

    def draw_celebrations(self):
        for c in self.confetti:
            c.update()
            c.draw(self.screen)
        
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        self.celebration_alpha = min(200, self.celebration_alpha + 3)
        self.celebration_surface.fill((255, 255, 255, self.celebration_alpha))
        self.screen.blit(self.celebration_surface, (0, 0))
        
        text = "VICTORY!"
        text_width = self.font_large.size(text)[0]
        base_x = self.WIDTH//2 - text_width//2
        
        for i, char in enumerate(text):
            hue = (pygame.time.get_ticks() // 50 + i * 30) % 360
            color = pygame.Color(0, 0, 0)
            color.hsva = (hue, 100, 100, 100)
            bounce = math.sin(pygame.time.get_ticks() / 200 + i) * 15
            char_surf = self.font_large.render(char, True, color)
            self.screen.blit(char_surf, (base_x + i * 70, self.HEIGHT//2 - 100 + bounce))
        
        pulse = math.sin(pygame.time.get_ticks() / 200) * 30 + 155
        restart_text = self.font_medium.render("Press R to restart", True, (pulse, pulse, pulse))
        restart_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def draw_help(self):
        help_surface = pygame.Surface((self.WIDTH-100, self.HEIGHT-100), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 220))
        pygame.draw.rect(help_surface, self.COLORS['WHITE'], 
                        (0, 0, self.WIDTH-100, self.HEIGHT-100), 2, border_radius=10)
        
        title = self.font_medium.render("How to Play", True, self.COLORS['WHITE'])
        help_surface.blit(title, (20, 20))
        
        instructions = [
            "Arrow Keys: Move your player (red)",
            "Click/Tap: Move toward clicked position",
            "Move AI Button/Space: Move A* AI (yellow) one step",
            "Undo AI Button/Shift+Space: Undo A* AI's last move",
            "Move Dijkstra Button: Move Dijkstra AI (orange) one step",
            "Undo Dijkstra Button: Undo Dijkstra AI's last move",
            "Auto AI Button: Toggle continuous A* AI movement",
            "Auto Dijkstra Button: Toggle continuous Dijkstra AI movement",
            "Reset Button: Start a new game",
            "Speed Slider: Adjust game speed",
            "Maze Size Slider: Change maze complexity",
            "",
            "Reach the blue goal to win!",
            "",
            "Press H to close this help"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font_small.render(line, True, self.COLORS['WHITE'])
            help_surface.blit(text, (20, 70 + i*30))
        
        self.screen.blit(help_surface, (50, 50))

    def handle_click(self, pos):
        if pos[1] < self.MAZE_OFFSET_Y:
            return
            
        grid_x = pos[0] // self.CELL_SIZE
        grid_y = (pos[1] - self.MAZE_OFFSET_Y) // self.CELL_SIZE
        
        if (0 <= grid_x < self.COLS and 
            0 <= grid_y < self.ROWS and 
            self.maze[grid_y][grid_x] == 0):
            
            path = self.a_star(self.player, (grid_x, grid_y))
            if path and len(path) > 0:
                dx = path[0][0] - self.player[0]
                dy = path[0][1] - self.player[1]
                self.move_player(dx, dy)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        # Check hover for all buttons
        self.move_ai_button.check_hover(mouse_pos)
        self.undo_ai_button.check_hover(mouse_pos)
        self.auto_ai_button.check_hover(mouse_pos)
        self.reset_button.check_hover(mouse_pos)
        self.move_dijkstra_button.check_hover(mouse_pos)
        self.undo_dijkstra_button.check_hover(mouse_pos)
        self.auto_dijkstra_button.check_hover(mouse_pos)
        self.help_button.check_hover(mouse_pos)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Button handling
            if self.move_ai_button.is_clicked(mouse_pos, event) and not self.game_over:
                self.move_ai()
            if self.undo_ai_button.is_clicked(mouse_pos, event) and not self.game_over:
                self.undo_ai_move()
            if self.move_dijkstra_button.is_clicked(mouse_pos, event) and not self.game_over:
                self.move_dijkstra()
            if self.undo_dijkstra_button.is_clicked(mouse_pos, event) and not self.game_over:
                self.undo_dijkstra_move()
            if self.reset_button.is_clicked(mouse_pos, event):
                self.reset_game()
            if self.help_button.is_clicked(mouse_pos, event):
                self.show_help = not self.show_help
            if self.auto_ai_button.is_clicked(mouse_pos, event):
                self.auto_ai = not self.auto_ai
                self.auto_ai_timer = 0
            if self.auto_dijkstra_button.is_clicked(mouse_pos, event):
                self.auto_dijkstra = not self.auto_dijkstra
                self.auto_dijkstra_timer = 0
            
            # Slider handling
            if self.speed_slider.handle_event(event):
                pass
            if self.maze_size_slider.handle_event(event):
                new_size = int(self.maze_size_slider.value)
                if new_size != self.ROWS:
                    self.ROWS = self.COLS = new_size
                    self.CELL_SIZE = min(30, 600 // self.ROWS)
                    self.reset_game()
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not self.show_help:
                self.handle_click(mouse_pos)
            
            if event.type == pygame.KEYDOWN and not self.show_help:
                if event.key == pygame.K_UP and not self.game_over:
                    self.move_player(0, -1)
                elif event.key == pygame.K_DOWN and not self.game_over:
                    self.move_player(0, 1)
                elif event.key == pygame.K_LEFT and not self.game_over:
                    self.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT and not self.game_over:
                    self.move_player(1, 0)
                elif event.key == pygame.K_SPACE and not self.game_over:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.undo_ai_move()
                    else:
                        self.move_ai()
                elif event.key == pygame.K_d and not self.game_over:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.undo_dijkstra_move()
                    else:
                        self.move_dijkstra()
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_a:
                    self.auto_ai = not self.auto_ai
                    self.auto_ai_timer = 0
                elif event.key == pygame.K_s:
                    self.auto_dijkstra = not self.auto_dijkstra
                    self.auto_dijkstra_timer = 0
        
        return True

    def update(self):
        dt = 1/60  # Fixed delta time for simplicity
        
        if self.auto_ai and not self.game_over:
            self.auto_ai_timer += dt
            if self.auto_ai_timer > 1.0 / (self.speed_slider.value / 2):
                self.move_ai()
                self.auto_ai_timer = 0
                
        if self.auto_dijkstra and not self.game_over:
            self.auto_dijkstra_timer += dt
            if self.auto_dijkstra_timer > 1.0 / (self.speed_slider.value / 2):
                self.move_dijkstra()
                self.auto_dijkstra_timer = 0
        
        if self.player_anim > 0:
            self.player_anim -= 1
            
        if self.ai_anim > 0:
            self.ai_anim -= 1
            
        if self.dijkstra_anim > 0:
            self.dijkstra_anim -= 1

    def draw(self):
        # Background
        self.screen.fill(self.COLORS['DARK_GRAY'])
        
        # Control panel background
        pygame.draw.rect(self.screen, self.COLORS['LIGHT_GRAY'], (0, 0, self.WIDTH, self.MAZE_OFFSET_Y))
        pygame.draw.rect(self.screen, self.COLORS['BLACK'], (0, self.MAZE_OFFSET_Y-2, self.WIDTH, 2))
        
        # Draw buttons
        self.move_ai_button.draw(self.screen, self.font_small)
        self.undo_ai_button.draw(self.screen, self.font_small)
        self.move_dijkstra_button.draw(self.screen, self.font_small)
        self.undo_dijkstra_button.draw(self.screen, self.font_small)
        self.reset_button.draw(self.screen, self.font_small)
        self.help_button.draw(self.screen, self.font_small)
        self.auto_ai_button.draw(self.screen, self.font_small)
        self.auto_dijkstra_button.draw(self.screen, self.font_small)
        
        # Draw sliders
        self.speed_slider.draw(self.screen, self.font_tiny)
        self.maze_size_slider.draw(self.screen, self.font_tiny)
        
        # Auto AI indicators
        if self.auto_ai:
            auto_text = self.font_tiny.render("A* AUTO", True, self.COLORS['GREEN'])
            self.screen.blit(auto_text, (self.auto_ai_button.rect.right + 10, 
                                       self.auto_ai_button.rect.centery - 10))
        if self.auto_dijkstra:
            auto_text = self.font_tiny.render("DIJKSTRA AUTO", True, self.COLORS['ORANGE'])
            self.screen.blit(auto_text, (self.auto_dijkstra_button.rect.right + 10, 
                                       self.auto_dijkstra_button.rect.centery - 10))
        
        if not self.game_over:
            self.draw_maze()
            self.draw_trails()  # Draw the trails before the agents
            self.draw_path()

            # Draw goal
            goal_rect = pygame.Rect(
                self.goal[0] * self.CELL_SIZE, 
                self.goal[1] * self.CELL_SIZE + self.MAZE_OFFSET_Y, 
                self.CELL_SIZE, self.CELL_SIZE
            )
            pygame.draw.rect(self.screen, self.COLORS['BLUE'], goal_rect)
            pulse_size = math.sin(pygame.time.get_ticks() / 500) * 3 + 1
            pygame.draw.rect(
                self.screen, (100, 200, 255), 
                (goal_rect.x + pulse_size, goal_rect.y + pulse_size, 
                 goal_rect.width - pulse_size*2, goal_rect.height - pulse_size*2)
            )
            
            # Draw A* AI with animation
            if self.ai_anim > 0:
                progress = 1 - (self.ai_anim / 10)
                anim_x = (self.ai_prev[0] * self.CELL_SIZE + 
                         (self.ai_target[0] - self.ai_prev[0]) * self.CELL_SIZE * progress)
                anim_y = (self.ai_prev[1] * self.CELL_SIZE + 
                         (self.ai_target[1] - self.ai_prev[1]) * self.CELL_SIZE * progress + 
                         self.MAZE_OFFSET_Y)
            else:
                anim_x = self.ai_position[0] * self.CELL_SIZE
                anim_y = self.ai_position[1] * self.CELL_SIZE + self.MAZE_OFFSET_Y
            
            # A* AI shadow
            pygame.draw.rect(
                self.screen, (50, 50, 50), 
                (anim_x + 3, anim_y + 3, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )
            # A* AI
            pygame.draw.rect(
                self.screen, self.COLORS['YELLOW'], 
                (anim_x, anim_y, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )
            
            # Draw Dijkstra's AI with animation
            if self.dijkstra_anim > 0:
                progress = 1 - (self.dijkstra_anim / 10)
                anim_x = (self.dijkstra_prev[0] * self.CELL_SIZE + 
                         (self.dijkstra_target[0] - self.dijkstra_prev[0]) * self.CELL_SIZE * progress)
                anim_y = (self.dijkstra_prev[1] * self.CELL_SIZE + 
                         (self.dijkstra_target[1] - self.dijkstra_prev[1]) * self.CELL_SIZE * progress + 
                         self.MAZE_OFFSET_Y)
            else:
                anim_x = self.dijkstra_position[0] * self.CELL_SIZE
                anim_y = self.dijkstra_position[1] * self.CELL_SIZE + self.MAZE_OFFSET_Y
            
            # Dijkstra's AI shadow
            pygame.draw.rect(
                self.screen, (50, 50, 50), 
                (anim_x + 3, anim_y + 3, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )
            # Dijkstra's AI
            pygame.draw.rect(
                self.screen, self.COLORS['ORANGE'], 
                (anim_x, anim_y, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )
            
            # Draw player with animation
            if self.player_anim > 0:
                progress = 1 - (self.player_anim / 10)
                anim_x = (self.player_prev[0] * self.CELL_SIZE + 
                         (self.player_target[0] - self.player_prev[0]) * self.CELL_SIZE * progress)
                anim_y = (self.player_prev[1] * self.CELL_SIZE + 
                         (self.player_target[1] - self.player_prev[1]) * self.CELL_SIZE * progress + 
                         self.MAZE_OFFSET_Y)
            else:
                anim_x = self.player[0] * self.CELL_SIZE
                anim_y = self.player[1] * self.CELL_SIZE + self.MAZE_OFFSET_Y
            
            # Player shadow
            pygame.draw.rect(
                self.screen, (50, 50, 50), 
                (anim_x + 3, anim_y + 3, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )
            # Player
            pygame.draw.rect(
                self.screen, self.COLORS['RED'], 
                (anim_x, anim_y, self.CELL_SIZE, self.CELL_SIZE), 
                border_radius=3
            )

            # Collision indicator
            if (self.player == self.ai_position or 
                self.player == self.dijkstra_position or 
                self.ai_position == self.dijkstra_position):
                collision_x = 0
                collision_y = 0
                collision_count = 0
                
                # Calculate average collision position if multiple collisions
                if self.player == self.ai_position:
                    collision_x += self.player[0] * self.CELL_SIZE + self.CELL_SIZE//2
                    collision_y += (self.player[1] * self.CELL_SIZE + 
                                self.MAZE_OFFSET_Y + self.CELL_SIZE//2)
                    collision_count += 1
                
                if self.player == self.dijkstra_position:
                    collision_x += self.player[0] * self.CELL_SIZE + self.CELL_SIZE//2
                    collision_y += (self.player[1] * self.CELL_SIZE + 
                                self.MAZE_OFFSET_Y + self.CELL_SIZE//2)
                    collision_count += 1
                
                if self.ai_position == self.dijkstra_position:
                    collision_x += self.ai_position[0] * self.CELL_SIZE + self.CELL_SIZE//2
                    collision_y += (self.ai_position[1] * self.CELL_SIZE + 
                                self.MAZE_OFFSET_Y + self.CELL_SIZE//2)
                    collision_count += 1
                
                # Calculate average position if multiple collisions
                if collision_count > 0:
                    collision_x = collision_x // collision_count
                    collision_y = collision_y // collision_count
                    
                    # Draw pulsing collision indicator
                    radius = math.sin(pygame.time.get_ticks() / 200) * 5 + 15
                    pygame.draw.circle(
                        self.screen, self.COLORS['GREEN'], 
                        (int(collision_x), int(collision_y)), 
                        int(radius), 2
                    )
        else:
            # Darken the maze in background
            darken = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            darken.fill((0, 0, 0, 150))
            self.screen.blit(darken, (0, 0))
        
        if self.game_over and self.victory:
            self.draw_celebrations()
        
        if self.show_help:
            self.draw_help()

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)

# Run the game
if __name__ == "__main__":
    game = MazeGame()
    game.run()
    pygame.quit()
    sys.exit()