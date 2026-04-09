# src/core/menu.py
import pygame
import math


class MainMenu:
    """Main menu screen with cyberpunk aesthetic"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.credit_font = pygame.font.Font(None, 20)
        
        # Menu options
        self.options = [
            "START SIMULATION",
            "SETTINGS",
            "QUIT"
        ]
        self.selected = 0
        
        # Animation
        self.time = 0
        self.particles = []
        self.generate_particles()
        
        # State
        self.active = True
        self.action = None
        
    def generate_particles(self):
        """Generate background particles for cyberpunk effect"""
        import random
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'speed': random.uniform(20, 60),
                'size': random.randint(1, 3),
                'color': random.choice([(0, 255, 255), (255, 0, 255), (100, 100, 255)])
            })
            
    def update(self, dt, events):
        """Update menu state"""
        self.time += dt
        
        # Update particles
        for particle in self.particles:
            particle['y'] += particle['speed'] * dt
            if particle['y'] > self.height:
                particle['y'] = -10
                
        # Handle input
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.select_option()
                    
    def select_option(self):
        """Handle menu selection"""
        if self.selected == 0:  # Start
            self.action = "start"
            self.active = False
        elif self.selected == 1:  # Settings
            self.action = "settings"
            # For now, just print
            print("Settings not implemented yet")
        elif self.selected == 2:  # Quit
            self.action = "quit"
            self.active = False
            
    def draw(self, screen):
        """Draw the menu"""
        # Background
        screen.fill((10, 0, 20))
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
        
        # Draw grid lines for cyberpunk effect
        grid_color = (30, 30, 60)
        for x in range(0, self.width, 50):
            pygame.draw.line(screen, grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(screen, grid_color, (0, y), (self.width, y), 1)
            
        # Title with glitch effect
        title_text = "ECHO RUNNER"
        
        # Glitch layers
        glitch_colors = [(255, 0, 255, 100), (0, 255, 255, 100), (255, 255, 255, 255)]
        for i, color in enumerate(glitch_colors):
            offset_x = math.sin(self.time * 3 + i) * 2
            offset_y = math.cos(self.time * 2 + i) * 1
            
            if len(color) == 4:
                title_surface = self.title_font.render(title_text, True, color[:3])
                title_surface.set_alpha(color[3])
            else:
                title_surface = self.title_font.render(title_text, True, color)
                
            title_rect = title_surface.get_rect(center=(self.width // 2 + offset_x, 150 + offset_y))
            screen.blit(title_surface, title_rect)
            
        # Subtitle
        subtitle = self.menu_font.render("SYSTEM CORRUPTION DETECTED", True, (150, 150, 255))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 220))
        screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        for i, option in enumerate(self.options):
            y_pos = 350 + i * 60
            
            if i == self.selected:
                # Selected option - animated
                pulse = abs(math.sin(self.time * 4))
                color = (int(100 + pulse * 155), int(255 - pulse * 100), 255)
                
                # Selection indicator
                indicator_points = [
                    (self.width // 2 - 150, y_pos),
                    (self.width // 2 - 130, y_pos - 10),
                    (self.width // 2 - 130, y_pos + 10)
                ]
                pygame.draw.polygon(screen, color, indicator_points)
                
                indicator_points = [
                    (self.width // 2 + 150, y_pos),
                    (self.width // 2 + 130, y_pos - 10),
                    (self.width // 2 + 130, y_pos + 10)
                ]
                pygame.draw.polygon(screen, color, indicator_points)
            else:
                color = (100, 100, 150)
                
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.width // 2, y_pos))
            screen.blit(text, text_rect)
            
        # Credits
        credit_text = "Your consciousness awaits..."
        credit = self.credit_font.render(credit_text, True, (80, 80, 100))
        credit_rect = credit.get_rect(center=(self.width // 2, self.height - 50))
        screen.blit(credit, credit_rect)
        
        # Instructions
        instructions = "↑↓ Navigate    ENTER Select    ESC Quit"
        inst_surface = self.credit_font.render(instructions, True, (100, 100, 120))
        inst_rect = inst_surface.get_rect(center=(self.width // 2, self.height - 20))
        screen.blit(inst_surface, inst_rect)


class PauseMenu:
    """Pause menu overlay"""
    
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        
        self.options = ["RESUME", "RESTART", "QUIT TO MENU"]
        self.selected = 0
        self.active = False
        self.action = None
        
    def toggle(self):
        """Toggle pause state"""
        self.active = not self.active
        if self.active:
            self.selected = 0
            self.action = None
        return self.active
        
    def update(self, events):
        """Update pause menu"""
        if not self.active:
            return
            
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.action = "resume"
                    self.active = False
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.select_option()
                    
    def select_option(self):
        """Handle pause menu selection"""
        if self.selected == 0:  # Resume
            self.action = "resume"
            self.active = False
        elif self.selected == 1:  # Restart
            self.action = "restart"
            self.active = False
        elif self.selected == 2:  # Quit to menu
            self.action = "menu"
            self.active = False
            
    def draw(self, screen):
        """Draw pause menu overlay"""
        if not self.active:
            return
            
        # Darken background
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 200))
        screen.blit(title, title_rect)
        
        # Options
        for i, option in enumerate(self.options):
            y_pos = 300 + i * 50
            
            if i == self.selected:
                color = (0, 255, 255)
                # Draw selection brackets
                bracket_left = self.font_medium.render("[", True, color)
                bracket_right = self.font_medium.render("]", True, color)
                screen.blit(bracket_left, (self.width // 2 - 120, y_pos - 15))
                screen.blit(bracket_right, (self.width // 2 + 105, y_pos - 15))
            else:
                color = (150, 150, 150)
                
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.width // 2, y_pos))
            screen.blit(text, text_rect)
