# src/systems/cutscene.py
import pygame
import random


class CutsceneManager:
    """Manages text-based cutscenes with timing and effects"""

    def __init__(self):
        self.active = False
        self.lines = []
        self.current_line_index = 0
        self.line_timer = 0.0
        self.line_duration = 2.5  # Default duration per line
        self.complete = False

        # Visual effects
        self.glitch_intensity = 0.0
        self.fade_alpha = 0
        self.fade_in = False
        self.fade_out = False

        # Callback when cutscene completes
        self.on_complete = None

    def start(self, lines, line_duration=2.5, glitch_intensity=0.3, on_complete=None):
        """Start a cutscene with given lines"""
        self.active = True
        self.lines = lines
        self.current_line_index = 0
        self.line_timer = 0.0
        self.line_duration = line_duration
        self.glitch_intensity = glitch_intensity
        self.complete = False
        self.fade_alpha = 0
        self.fade_in = True
        self.fade_out = False
        self.on_complete = on_complete

    def skip(self):
        """Skip to end of cutscene"""
        self.current_line_index = len(self.lines) - 1
        self.line_timer = self.line_duration

    def update(self, dt):
        """Update cutscene timing"""
        if not self.active:
            return

        # Handle fade in
        if self.fade_in:
            self.fade_alpha += dt * 300
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_in = False

        # Handle fade out
        if self.fade_out:
            self.fade_alpha -= dt * 300
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_out = False
                self.active = False
                self.complete = True
                if self.on_complete:
                    self.on_complete()
                return

        # Progress through lines
        self.line_timer += dt
        if self.line_timer >= self.line_duration:
            self.line_timer = 0.0
            self.current_line_index += 1

            # Check if cutscene is complete
            if self.current_line_index >= len(self.lines):
                self.fade_out = True
                self.current_line_index = len(self.lines) - 1

    def draw(self, screen):
        """Draw current cutscene line with effects"""
        if not self.active or len(self.lines) == 0:
            return

        # Get current line
        if self.current_line_index < len(self.lines):
            line = self.lines[self.current_line_index]
        else:
            line = self.lines[-1]

        # Create font
        font = pygame.font.Font(None, 48)

        # Render with glitch effect
        if self.glitch_intensity > 0:
            # Random glitch offset
            offset_x = random.randint(0, int(self.glitch_intensity * 10))
            offset_y = random.randint(-int(self.glitch_intensity * 5), int(self.glitch_intensity * 5))

            # Glitch colors
            glitch_colors = [
                (255, 0, 255),  # Magenta
                (0, 255, 255),  # Cyan
                (255, 255, 255) # White
            ]

            # Draw glitchy text layers
            for i, color in enumerate(glitch_colors):
                glitch_offset = (offset_x * i, offset_y * i)
                text_surface = font.render(line, True, color)
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2 + glitch_offset[0],
                                                          screen.get_height() // 2 + glitch_offset[1]))
                text_surface.set_alpha(int(self.fade_alpha * 0.6))
                screen.blit(text_surface, text_rect)
        else:
            # Normal text
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            text_surface.set_alpha(self.fade_alpha)
            screen.blit(text_surface, text_rect)


class GlitchText:
    """Renders text with glitch effects for dramatic moments"""

    def __init__(self, text, pos, font_size=64, color=(255, 255, 255)):
        self.text = text
        self.pos = pos
        self.font_size = font_size
        self.color = color
        self.glitch_timer = 0.0
        self.visible = True

    def update(self, dt):
        """Update glitch animation"""
        self.glitch_timer += dt

    def draw(self, screen):
        """Draw text with glitch effect"""
        if not self.visible:
            return

        font = pygame.font.Font(None, self.font_size)

        # Random glitch chance
        if random.random() < 0.3:
            # Draw glitched version
            glitch_chars = ['@', '#', '$', '%', '&', '*']
            glitched_text = ''.join(
                random.choice(glitch_chars) if random.random() < 0.1 else c
                for c in self.text
            )
            text_surface = font.render(glitched_text, True, self.color)
        else:
            text_surface = font.render(self.text, True, self.color)

        # Random offset for jitter effect
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)

        text_rect = text_surface.get_rect(center=(self.pos[0] + offset_x, self.pos[1] + offset_y))
        screen.blit(text_surface, text_rect)

        # Draw RGB split layers occasionally
        if random.random() < 0.2:
            # Magenta layer
            magenta_surf = font.render(self.text, True, (255, 0, 255))
            magenta_surf.set_alpha(100)
            screen.blit(magenta_surf, (text_rect.x - 3, text_rect.y))

            # Cyan layer
            cyan_surf = font.render(self.text, True, (0, 255, 255))
            cyan_surf.set_alpha(100)
            screen.blit(cyan_surf, (text_rect.x + 3, text_rect.y))
