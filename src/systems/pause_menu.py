# src/systems/pause_menu.py
import pygame
from settings import WIDTH, HEIGHT


class PauseMenu:
    """Pause menu overlay for the game"""

    def __init__(self):
        self.active = False
        self.selected = 0
        self.options = ["RESUME", "RESTART LEVEL", "QUIT"]

        # Fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_hint = pygame.font.Font(None, 32)

        # Animation
        self.pulse_timer = 0.0

    def toggle(self):
        """Toggle pause menu on/off"""
        self.active = not self.active
        if self.active:
            self.selected = 0  # Reset selection when opening
        return self.active

    def update(self, dt):
        """Update pause menu animations"""
        if not self.active:
            return

        self.pulse_timer += dt

    def handle_input(self, event):
        """Handle keyboard input and return action"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
                return None
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "RESUME"

        return None

    def draw(self, screen):
        """Draw the pause menu overlay"""
        if not self.active:
            return

        # Semi-transparent dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Title with cyan glow
        title_text = self.font_title.render("PAUSED", True, (0, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        screen.blit(title_text, title_rect)

        # Subtitle
        subtitle = self.font_hint.render("SIMULATION SUSPENDED", True, (150, 150, 200))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        screen.blit(subtitle, subtitle_rect)

        # Menu options
        import math
        pulse = abs(math.sin(self.pulse_timer * 4))

        for i, option in enumerate(self.options):
            y_pos = HEIGHT // 2 + 20 + (i * 60)

            if i == self.selected:
                # Selected option - animated pulse
                color = (int(100 + pulse * 155), int(200 + pulse * 55), 255)

                # Draw selection brackets
                bracket_left = self.font_option.render(">", True, color)
                bracket_right = self.font_option.render("<", True, color)
                screen.blit(bracket_left, (WIDTH // 2 - 150, y_pos - 5))
                screen.blit(bracket_right, (WIDTH // 2 + 130, y_pos - 5))
            else:
                color = (120, 120, 150)

            # Draw option text
            option_text = self.font_option.render(option, True, color)
            option_rect = option_text.get_rect(center=(WIDTH // 2, y_pos))
            screen.blit(option_text, option_rect)

        # Instructions at bottom
        instructions = "↑↓ Navigate  •  ENTER Select  •  ESC Resume"
        inst_text = self.font_hint.render(instructions, True, (100, 100, 120))
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        screen.blit(inst_text, inst_rect)
