# src/world/tiles.py
import pygame
import math


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.original_image = pygame.Surface((width, 20), pygame.SRCALPHA)

        # neon bar
        base_color = (0, 255, 255)
        for i in range(20):
            alpha = int(255 * (1 - i / 20))
            pygame.draw.rect(self.original_image, (*base_color, alpha), (0, i, width, 1))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))

        # Fading properties
        self.fade_alpha = 1.0  # 1.0 = fully visible, 0.0 = invisible
        self.is_fading = False
        self.fade_duration = 3.0  # How long it takes to fade out completely
        self.fade_timer = 0.0
        self.is_solid = True  # Whether player can collide with it

        # Warning glow properties
        self.warning_threshold = 3.0  # Start warning 3 seconds before fade
        self.glow_timer = 0.0
        self.glow_intensity = 0.0
        self.warning_active = False

        # Particle callback (set by game.py)
        self.on_fade_complete = None

    def start_fade(self):
        """Begin the platform fade-out process"""
        self.is_fading = True
        self.fade_timer = 0.0

    def update(self, dt):
        """Update platform fade state and warning glow"""
        if self.is_fading:
            self.fade_timer += dt
            # Calculate fade progress (0.0 to 1.0)
            fade_progress = min(self.fade_timer / self.fade_duration, 1.0)
            self.fade_alpha = 1.0 - fade_progress

            # Warning glow activates in last 3 seconds
            time_remaining = self.fade_duration - self.fade_timer
            if time_remaining <= self.warning_threshold and time_remaining > 0:
                self.warning_active = True
                self.glow_timer += dt

                # Pulse frequency increases as time runs out
                # 1 Hz at 3 seconds -> 3 Hz at 0 seconds
                frequency = 1 + (2 * (1.0 - (time_remaining / self.warning_threshold)))
                self.glow_intensity = abs(math.sin(self.glow_timer * frequency * math.pi))
            else:
                self.warning_active = False

            # Platform becomes non-solid at 50% fade
            if fade_progress >= 0.5:
                self.is_solid = False

            # Update visual alpha
            self.image = self.original_image.copy()
            self.image.set_alpha(int(self.fade_alpha * 255))

            # Trigger particle burst when fully faded
            if fade_progress >= 1.0 and self.on_fade_complete:
                self.on_fade_complete(self.rect.center)

    def draw(self, screen: pygame.Surface, camera_x: int):
        # Draw warning glow if active
        if self.warning_active and self.glow_intensity > 0:
            # Color pulsing between yellow and red
            time_remaining = self.fade_duration - self.fade_timer
            color_blend = 1.0 - (time_remaining / self.warning_threshold)

            red = 255
            green = int(255 * (1.0 - color_blend))
            blue = 0

            glow_color = (red, green, blue)

            # Draw outer glow rect (additive blending)
            glow_alpha = int(120 + 60 * self.glow_intensity)
            glow_rect = self.rect.inflate(8, 8)

            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_surf.fill((*glow_color, glow_alpha))

            screen.blit(glow_surf,
                       (glow_rect.x - camera_x, glow_rect.y),
                       special_flags=pygame.BLEND_ADD)

        # Draw platform
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))
