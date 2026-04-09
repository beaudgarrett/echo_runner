# src/systems/hud.py
import pygame
import math


class HUD:
    """Enhanced HUD with visual indicators"""
    
    def __init__(self):
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # Animation timers
        self.pulse_timer = 0
        self.flash_timer = 0
        self.message_queue = []
        
    def draw(self, screen, player, level_manager, invincibility_mode=False, level_timer=None, easter_egg_count=0):
        """Draw all HUD elements"""
        width, height = screen.get_size()

        # Draw lives (hearts)
        self.draw_lives(screen, player.lives, 20, 60)

        # Draw dash charges (energy bars)
        self.draw_dash_charges(screen, player.dash_charges, player.max_dash_charges,
                              width - 200, 20)

        # Draw stability meter
        self.draw_stability(screen, level_manager.stability, 20, 20)

        # Draw level indicator
        self.draw_level_indicator(screen, level_manager.level, width // 2, 20)

        # Draw timer (if provided)
        if level_timer is not None:
            self.draw_timer(screen, level_timer, width // 2, 60)

        # Draw easter egg counter (if any collected)
        if easter_egg_count > 0:
            self.draw_easter_eggs(screen, easter_egg_count, 20, 110)

        # Draw speed boost indicator if active
        if hasattr(player, 'speed_boost_timer') and player.speed_boost_timer > 0:
            self.draw_speed_boost(screen, player.speed_boost_timer, width - 200, 60)

        # Draw invincibility mode indicator if active
        if invincibility_mode:
            self.draw_invincibility(screen, width - 200, 100)

        # Draw messages
        self.draw_messages(screen)
        
    def draw_lives(self, screen, lives, x, y):
        """Draw heart icons for lives"""
        for i in range(3):
            heart_x = x + i * 35
            if i < lives:
                # Full heart
                self.draw_heart(screen, heart_x, y, (255, 50, 100))
            else:
                # Empty heart
                self.draw_heart(screen, heart_x, y, (100, 30, 50))
                
    def draw_heart(self, screen, x, y, color):
        """Draw a single heart"""
        # Simple heart shape
        pygame.draw.circle(screen, color, (x + 6, y + 8), 6)
        pygame.draw.circle(screen, color, (x + 18, y + 8), 6)
        points = [(x, y + 12), (x + 12, y + 24), (x + 24, y + 12)]
        pygame.draw.polygon(screen, color, points)
        
    def draw_dash_charges(self, screen, charges, max_charges, x, y):
        """Draw battery-style icons for dash charges - hot pink retro style"""
        # Label
        label = self.font_small.render("DASH", True, (255, 50, 255))
        screen.blit(label, (x, y - 8))

        # Battery icons - hot pink retro style
        battery_width = 22
        battery_height = 32
        spacing = 28
        start_x = x

        for i in range(max_charges):
            battery_x = start_x + i * spacing
            battery_y = y + 15

            # Battery body (main rectangle)
            body_rect = pygame.Rect(battery_x, battery_y, battery_width, battery_height)

            # Battery terminal (small nub on top)
            terminal_width = 10
            terminal_height = 4
            terminal_x = battery_x + (battery_width - terminal_width) // 2
            terminal_y = battery_y - terminal_height
            terminal_rect = pygame.Rect(terminal_x, terminal_y, terminal_width, terminal_height)

            if i < charges:
                # Filled battery - hot pink with cyan glow
                # Outer glow
                glow_color = (0, 255, 255, 80)
                glow_surf = pygame.Surface((battery_width + 8, battery_height + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, glow_color, (0, 0, battery_width + 8, battery_height + 8), border_radius=3)
                screen.blit(glow_surf, (battery_x - 4, battery_y - 4))

                # Main body - hot pink
                pygame.draw.rect(screen, (255, 50, 255), body_rect, border_radius=3)
                # Inner fill - brighter pink
                inner_rect = pygame.Rect(battery_x + 3, battery_y + 3, battery_width - 6, battery_height - 6)
                pygame.draw.rect(screen, (255, 100, 255), inner_rect, border_radius=2)

                # Terminal
                pygame.draw.rect(screen, (255, 50, 255), terminal_rect, border_radius=1)

                # Energy bars inside (3 horizontal bars)
                for bar_idx in range(3):
                    bar_y_pos = battery_y + 7 + bar_idx * 8
                    bar_rect = pygame.Rect(battery_x + 5, bar_y_pos, battery_width - 10, 5)
                    pygame.draw.rect(screen, (255, 255, 50), bar_rect, border_radius=1)
            else:
                # Empty battery - dark gray outline
                pygame.draw.rect(screen, (80, 40, 80), body_rect, 2, border_radius=3)
                pygame.draw.rect(screen, (80, 40, 80), terminal_rect, border_radius=1)
                
    def draw_stability(self, screen, stability, x, y):
        """Draw stability meter"""
        # Background
        bg_width = 200
        bg_height = 24
        pygame.draw.rect(screen, (30, 30, 60), (x, y, bg_width, bg_height))
        
        # Stability bar
        fill_width = int((stability / 100) * bg_width)
        
        # Color based on stability level
        if stability < 30:
            color = (100, 150, 255)
        elif stability < 70:
            color = (150, 100, 255)
        else:
            color = (255, 100, 150)
            
        if fill_width > 0:
            pygame.draw.rect(screen, color, (x, y, fill_width, bg_height))
        
        # Corruption effect overlay
        if stability > 70:
            for i in range(int(stability / 10)):
                glitch_x = x + (i * 20) % bg_width
                pygame.draw.rect(screen, (255, 0, 255, 50), (glitch_x, y, 2, bg_height))
        
        # Border
        pygame.draw.rect(screen, (200, 200, 255), (x, y, bg_width, bg_height), 2)
        
        # Text
        text = self.font_medium.render(f"STABILITY: {int(stability)}%", True, (255, 255, 255))
        screen.blit(text, (x + 5, y + 2))
        
    def draw_level_indicator(self, screen, level, x, y):
        """Draw current level indicator"""
        level_names = {
            1: "CLEAN SIM",
            2: "CORRUPT SECTOR",
            3: "ARCHON CORE"
        }
        
        level_name = level_names.get(level, f"LEVEL {level}")
        
        # Create glitchy text effect for higher levels
        if level >= 2:
            # Draw multiple offset versions for glitch effect
            colors = [(255, 0, 255), (0, 255, 255), (255, 255, 255)]
            for i, color in enumerate(colors):
                offset = i - 1
                text = self.font_large.render(level_name, True, color)
                text.set_alpha(100)
                text_rect = text.get_rect(center=(x + offset * 2, y))
                screen.blit(text, text_rect)
        
        # Main text
        text = self.font_large.render(level_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
        
    def draw_speed_boost(self, screen, timer, x, y):
        """Draw speed boost indicator"""
        # Lightning bolt icon
        points = [(x + 10, y + 5), (x, y + 15), (x + 8, y + 15), 
                 (x, y + 25), (x + 20, y + 10), (x + 12, y + 10)]
        
        # Pulse effect
        self.pulse_timer += 0.1
        pulse = abs(math.sin(self.pulse_timer * 3))
        color = (255, 255, int(100 + pulse * 155))
        
        pygame.draw.polygon(screen, color, points)
        
        # Timer text
        text = self.font_small.render(f"{timer:.1f}s", True, color)
        screen.blit(text, (x + 25, y + 8))

    def draw_invincibility(self, screen, x, y):
        """Draw invincibility mode indicator"""
        # Pulsing shield icon
        pulse = abs(math.sin(self.pulse_timer * 4))

        # Shield shape (hexagon)
        shield_center_x = x + 20
        shield_center_y = y + 15
        shield_radius = 15 + int(pulse * 3)

        shield_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            px = shield_center_x + math.cos(angle) * shield_radius
            py = shield_center_y + math.sin(angle) * shield_radius
            shield_points.append((px, py))

        # Glow effect
        glow_color = (50, 255, 50, int(100 + pulse * 155))
        glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        for i in range(3):
            scale = 1.0 + i * 0.15
            glow_points = []
            for px, py in shield_points:
                dx = px - shield_center_x
                dy = py - shield_center_y
                glow_points.append((shield_center_x + dx * scale, shield_center_y + dy * scale))
            pygame.draw.polygon(glow_surf, (50, 255, 50, 40), glow_points, 2)
        screen.blit(glow_surf, (x - 5, y - 5))

        # Main shield
        shield_color = (50, 255, 50)
        pygame.draw.polygon(screen, shield_color, shield_points, 3)

        # Inner detail
        inner_points = []
        for px, py in shield_points:
            dx = px - shield_center_x
            dy = py - shield_center_y
            inner_points.append((shield_center_x + dx * 0.6, shield_center_y + dy * 0.6))
        pygame.draw.polygon(screen, (100, 255, 100), inner_points, 2)

        # Text label
        text = self.font_small.render("INVINCIBLE", True, (50, 255, 50))
        screen.blit(text, (x + 45, y + 5))

    def add_message(self, text, color=(255, 255, 255), duration=2.0):
        """Add a temporary message to display"""
        self.message_queue.append({
            'text': text,
            'color': color,
            'timer': duration,
            'alpha': 255
        })
        
    def draw_messages(self, screen):
        """Draw temporary messages"""
        width = screen.get_width()
        y_offset = 100
        
        # Update and draw messages
        remaining = []
        for msg in self.message_queue:
            msg['timer'] -= 0.016  # Approximate frame time
            
            if msg['timer'] > 0:
                # Fade out in last 0.5 seconds
                if msg['timer'] < 0.5:
                    msg['alpha'] = int(msg['timer'] * 2 * 255)
                
                text = self.font_medium.render(msg['text'], True, msg['color'])
                text.set_alpha(msg['alpha'])
                text_rect = text.get_rect(center=(width // 2, y_offset))
                screen.blit(text, text_rect)
                
                y_offset += 35
                remaining.append(msg)
                
        self.message_queue = remaining

    def draw_timer(self, screen, time_seconds, x, y):
        """Draw speed run timer"""
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        milliseconds = int((time_seconds % 1) * 100)

        time_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

        # Draw with cyan color
        timer_text = self.font_small.render(time_str, True, (100, 255, 255))
        timer_rect = timer_text.get_rect(center=(x, y))

        # Add subtle glow
        glow_text = self.font_small.render(time_str, True, (50, 150, 150))
        glow_text.set_alpha(80)
        glow_rect = glow_text.get_rect(center=(x, y))
        screen.blit(glow_text, glow_rect.inflate(2, 2))

        screen.blit(timer_text, timer_rect)

    def draw_easter_eggs(self, screen, count, x, y):
        """Draw easter egg collection counter"""
        # Draw small golden egg icon
        egg_size = 15
        pygame.draw.ellipse(screen, (255, 215, 0), (x, y, egg_size, egg_size + 3))
        pygame.draw.ellipse(screen, (255, 235, 150), (x + 3, y + 2, egg_size - 6, egg_size - 3))

        # Draw count
        count_text = self.font_small.render(f"{count}/3", True, (255, 215, 0))
        screen.blit(count_text, (x + egg_size + 5, y))

    def update(self, dt):
        """Update HUD animations"""
        self.pulse_timer += dt
        self.flash_timer += dt
