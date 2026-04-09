# src/systems/tutorial.py
import pygame
import math


class Tutorial:
    """Tutorial overlay system that displays control instructions"""

    def __init__(self):
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.timer = 0.0
        self.duration = 60.0  # 60 second tutorial (1 minute)
        self.active = True
        self.can_skip = False  # Set externally by game

        # Tutorial steps with timing - each step is 12 seconds for better readability
        self.steps = [
            {
                "start": 0.0,
                "end": 12.0,
                "title": "WELCOME TO ECHO RUNNER",
                "text": [
                    "You are trapped in a corrupted simulation.",
                    "Jump on drones to terminate them.",
                    "Everything else will destroy you instantly."
                ]
            },
            {
                "start": 12.0,
                "end": 24.0,
                "title": "BASIC MOVEMENT",
                "text": [
                    "WASD or ARROW KEYS - Move left/right",
                    "SPACE or W or UP - Jump (press again in air to DOUBLE JUMP)",
                    "Stay on the glowing cyan platforms!"
                ]
            },
            {
                "start": 24.0,
                "end": 36.0,
                "title": "DASH ABILITY",
                "text": [
                    "SHIFT - Dash forward (5 charges)",
                    "Dashing helps you escape drones",
                    "Use it to cover large distances quickly"
                ]
            },
            {
                "start": 36.0,
                "end": 48.0,
                "title": "ENERGY DRINKS",
                "text": [
                    "Collect Ben Newtons White Monsters to refill dash charges",
                    "Pink batteries in the HUD show your dash count",
                    "You have 3 lives - avoid drones!"
                ]
            },
            {
                "start": 48.0,
                "end": 60.0,
                "title": "OBJECTIVE",
                "text": [
                    "Survive until STABILITY reaches 100%",
                    "Each level increases in difficulty",
                    "The final boss ARCHON awaits at Level 3..."
                ]
            }
        ]

    def update(self, dt):
        """Update tutorial timer"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False

    def is_complete(self):
        """Check if tutorial is finished"""
        return not self.active

    def get_current_step(self):
        """Get the current tutorial step based on timer"""
        for step in self.steps:
            if step["start"] <= self.timer < step["end"]:
                return step
        return None

    def draw(self, screen):
        """Draw tutorial overlay"""
        if not self.active:
            return

        step = self.get_current_step()
        if not step:
            return

        width, height = screen.get_size()

        # Semi-transparent dark overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Calculate fade in/out based on step timing
        step_progress = (self.timer - step["start"]) / (step["end"] - step["start"])
        if step_progress < 0.2:
            alpha = int(step_progress * 5 * 255)
        elif step_progress > 0.8:
            alpha = int((1.0 - step_progress) * 5 * 255)
        else:
            alpha = 255

        # Draw title
        title_surf = self.font_large.render(step["title"], True, (0, 255, 255))
        title_surf.set_alpha(alpha)
        title_rect = title_surf.get_rect(center=(width // 2, height // 2 - 100))
        screen.blit(title_surf, title_rect)

        # Draw text lines
        y_offset = height // 2 - 20
        for i, line in enumerate(step["text"]):
            # Pulse effect
            pulse = abs(math.sin(self.timer * 3 + i * 0.5))
            color = (
                int(100 + pulse * 155),
                int(200 + pulse * 55),
                int(200 + pulse * 55)
            )

            text_surf = self.font_medium.render(line, True, color)
            text_surf.set_alpha(alpha)
            text_rect = text_surf.get_rect(center=(width // 2, y_offset + i * 40))
            screen.blit(text_surf, text_rect)

        # Draw progress bar
        bar_width = 400
        bar_height = 8
        bar_x = (width - bar_width) // 2
        bar_y = height - 80

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

        # Progress fill
        fill_width = int((self.timer / self.duration) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 255, 255), (bar_x, bar_y, fill_width, bar_height), border_radius=4)

        # Timer text
        time_left = max(0, self.duration - self.timer)
        timer_text = self.font_small.render(f"Tutorial: {time_left:.1f}s", True, (150, 150, 150))
        timer_rect = timer_text.get_rect(center=(width // 2, bar_y - 20))
        screen.blit(timer_text, timer_rect)

        # Skip instruction - show different text based on whether skip is allowed
        if self.can_skip:
            skip_text = self.font_small.render("Press ENTER to skip", True, (100, 100, 100))
        else:
            skip_text = self.font_small.render("Press K for level select", True, (100, 100, 100))
        skip_rect = skip_text.get_rect(center=(width // 2, bar_y + 30))
        screen.blit(skip_text, skip_rect)
