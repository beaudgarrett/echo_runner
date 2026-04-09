# src/systems/font_fx.py
"""
Enhanced Visual Feedback - Electronic Font Effects
Custom text rendering with glitch, hue-shift, and glow effects
"""
import pygame
import random
import math


def render_glitch_text(screen, text, font, pos, base_color, flicker_intensity=0.3, hue_cycle=0.0):
    """
    Render text with glitch effects (data desync, hue shift, color separation)

    Args:
        screen: Pygame surface to draw on
        text: String to render
        font: Pygame font object
        pos: (x, y) position (center)
        base_color: (r, g, b) base color
        flicker_intensity: 0.0-1.0, amount of random offset
        hue_cycle: Time-based value for color cycling
    """
    # Calculate hue-shifted color
    shift_amount = int(30 * math.sin(hue_cycle))
    shifted_color = (
        max(0, min(255, base_color[0] + shift_amount)),
        max(0, min(255, base_color[1] - shift_amount)),
        max(0, min(255, base_color[2] + shift_amount))
    )

    # Random horizontal jitter (data desync)
    jitter_x = random.randint(-int(2 * flicker_intensity), int(2 * flicker_intensity))
    jitter_y = random.randint(-int(1 * flicker_intensity), int(1 * flicker_intensity))

    # RGB channel separation for glitch effect
    if flicker_intensity > 0.5:
        # Red channel offset
        red_surf = font.render(text, True, (shifted_color[0], 0, 0))
        red_surf.set_alpha(180)
        red_pos = (pos[0] + jitter_x - 2, pos[1] + jitter_y)
        screen.blit(red_surf, red_pos, special_flags=pygame.BLEND_ADD)

        # Cyan channel offset
        cyan_surf = font.render(text, True, (0, shifted_color[1], shifted_color[2]))
        cyan_surf.set_alpha(180)
        cyan_pos = (pos[0] + jitter_x + 2, pos[1] + jitter_y)
        screen.blit(cyan_surf, cyan_pos, special_flags=pygame.BLEND_ADD)

    # Main text
    main_surf = font.render(text, True, shifted_color)
    main_pos = (pos[0] + jitter_x, pos[1] + jitter_y)
    screen.blit(main_surf, main_pos)


def render_glow_text(screen, text, font, pos, color, glow_strength=3):
    """
    Render text with neon glow effect (multiple layered outlines)

    Args:
        screen: Pygame surface to draw on
        text: String to render
        font: Pygame font object
        pos: (x, y) position (center)
        color: (r, g, b) color
        glow_strength: Number of glow layers (1-5)
    """
    # Render glow layers (decreasing alpha)
    for i in range(glow_strength, 0, -1):
        glow_surf = font.render(text, True, color)
        alpha = int(255 / (i + 1))
        glow_surf.set_alpha(alpha)

        # Offset outward
        for dx in range(-i, i + 1):
            for dy in range(-i, i + 1):
                if dx != 0 or dy != 0:
                    glow_pos = (pos[0] + dx, pos[1] + dy)
                    screen.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ADD)

    # Main text (solid core)
    main_surf = font.render(text, True, color)
    screen.blit(main_surf, pos)


def render_static_overlay(screen, alpha=30):
    """
    Add animated noise pattern to simulate CRT interference

    Args:
        screen: Pygame surface to draw on
        alpha: Opacity of static (0-255)
    """
    width, height = screen.get_size()
    static_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Generate random noise pixels
    for _ in range(width * height // 100):  # Sparse static
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        brightness = random.randint(0, 255)
        static_surf.set_at((x, y), (brightness, brightness, brightness, alpha))

    screen.blit(static_surf, (0, 0))


class DashGainedText:
    """Displays 'DASH GAINED' notification"""

    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 1.5
        self.font = None
        self.pos = (0, 0)

    def trigger(self, font, pos):
        """Activate notification"""
        self.active = True
        self.timer = 0.0
        self.font = font
        self.pos = pos

    def update(self, dt):
        """Update timer"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen):
        """Draw notification"""
        if not self.active or not self.font:
            return

        # Calculate alpha fade
        if self.timer < 0.3:
            alpha = int(255 * (self.timer / 0.3))
        else:
            alpha = int(255 * (1.0 - ((self.timer - 0.3) / (self.duration - 0.3))))

        # Electric cyan color
        color = (0, 255, 255)

        # Float upward
        y_offset = -int(self.timer * 30)

        # Render with glow
        text_surf = self.font.render("DASH GAINED", True, color)
        text_surf.set_alpha(alpha)

        pos = (self.pos[0], self.pos[1] + y_offset)
        screen.blit(text_surf, pos, special_flags=pygame.BLEND_ADD)


class SystemWarningText:
    """Displays system warnings (corruption surge)"""

    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 2.0
        self.font = None
        self.text = ""
        self.flicker_timer = 0.0

    def trigger(self, font, text):
        """Activate warning"""
        self.active = True
        self.timer = 0.0
        self.font = font
        self.text = text
        self.flicker_timer = 0.0

    def update(self, dt):
        """Update timer and flicker"""
        if self.active:
            self.timer += dt
            self.flicker_timer += dt

            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen):
        """Draw warning with scanline effect"""
        if not self.active or not self.font:
            return

        # Flicker alpha
        alpha = int(200 + 55 * abs(math.sin(self.flicker_timer * 10)))

        # Cyan color with flicker
        color = (0, 255, 255)

        # Render text
        text_surf = self.font.render(self.text, True, color)
        text_surf.set_alpha(alpha)

        # Center position
        width, height = screen.get_size()
        pos = (width // 2 - text_surf.get_width() // 2, height - 100)

        # Horizontal scanline jitter
        jitter = random.randint(-2, 2)
        pos = (pos[0] + jitter, pos[1])

        screen.blit(text_surf, pos, special_flags=pygame.BLEND_ADD)

        # Draw scanline overlay
        scanline_surf = pygame.Surface((text_surf.get_width(), 2), pygame.SRCALPHA)
        scanline_surf.fill((0, 255, 255, 100))
        scanline_y = int((self.flicker_timer * 50) % text_surf.get_height())
        screen.blit(scanline_surf, (pos[0], pos[1] + scanline_y))
