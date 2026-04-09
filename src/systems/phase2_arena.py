# src/systems/phase2_arena.py
"""
Phase 2 Boss Arena - Rotating Platform System
One large platform that splits into two rotating platforms after 15 seconds
"""
import pygame
import math
from src.world.tiles import Platform


class Phase2Arena:
    """Manages the special Phase 2 boss arena with rotating platforms"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Arena state - MUST start inactive
        self.active = False
        self.timer = 0.0
        self.split_time = 15.0  # Split after 15 seconds

        # Platform system - MUST start empty
        self.platforms = pygame.sprite.Group()
        self.single_platform = None  # Initial large platform
        self.rotating_platforms = []  # Two platforms after split

        # Rotation parameters
        self.rotation_angle = 0.0
        self.rotation_speed = 0.3  # Radians per second
        self.rotation_radius = 200  # Distance from center
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2 + 100  # Lower center for better view
        self.spiral_center = pygame.Vector2(self.center_x, self.center_y)  # For boss spiral

        # Split animation
        self.is_split = False
        self.split_progress = 0.0

        # Ensure platforms start completely empty
        self.platforms.empty()
        self.rotating_platforms.clear()
        self.single_platform = None

    def activate(self):
        """Activate Phase 2 arena and create initial platform"""
        self.active = True
        self.timer = 0.0
        self.is_split = False
        self.split_progress = 0.0

        # Clear existing platforms
        self.platforms.empty()
        self.rotating_platforms.clear()

        # Create one large central platform
        platform_width = 600
        platform_x = self.center_x - platform_width // 2
        platform_y = self.center_y

        self.single_platform = Platform(platform_x, platform_y, platform_width)
        # Disable fading for arena platforms
        self.single_platform.is_fading = False
        self.platforms.add(self.single_platform)

        print("PHASE 2 ARENA ACTIVATED - One large platform")

    def update(self, dt):
        """Update arena state and platform positions"""
        if not self.active:
            return

        self.timer += dt

        # Check if we should split
        if self.timer >= self.split_time and not self.is_split:
            self.trigger_split()

        # Update rotation if split
        if self.is_split:
            self.rotation_angle += self.rotation_speed * dt

            # Update platform positions
            for i, platform in enumerate(self.rotating_platforms):
                # Each platform is 180 degrees apart
                angle = self.rotation_angle + (i * math.pi)

                # Calculate position on circle
                platform.rect.x = int(self.center_x + math.cos(angle) * self.rotation_radius - platform.rect.width // 2)
                platform.rect.y = int(self.center_y + math.sin(angle) * self.rotation_radius - platform.rect.height // 2)

        # Update platform visual effects
        for platform in self.platforms:
            platform.update(dt)

    def trigger_split(self):
        """Split the single platform into two rotating platforms"""
        print("PHASE 2 ARENA - PLATFORM SPLIT!")
        self.is_split = True

        # Remove single platform
        if self.single_platform:
            self.platforms.remove(self.single_platform)
            self.single_platform = None

        # Create two platforms
        platform_width = 300

        for i in range(2):
            # Initial positions (top and bottom)
            angle = i * math.pi  # 0 and π
            platform_x = int(self.center_x + math.cos(angle) * self.rotation_radius - platform_width // 2)
            platform_y = int(self.center_y + math.sin(angle) * self.rotation_radius - 10)

            platform = Platform(platform_x, platform_y, platform_width)
            platform.is_fading = False  # Never fade in arena
            self.platforms.add(platform)
            self.rotating_platforms.append(platform)

        print(f"Created {len(self.rotating_platforms)} rotating platforms")

    def draw(self, screen, camera_x):
        """Draw all arena platforms"""
        # CRITICAL: Never draw if arena is not active
        if not self.active:
            return

        for platform in self.platforms:
            platform.draw(screen, int(camera_x))

        # Draw arena boundary indicator (visual only)
        if self.is_split:
            # Draw rotation path circle
            pygame.draw.circle(
                screen,
                (50, 50, 100, 100),  # Dark blue, semi-transparent
                (self.center_x - int(camera_x), self.center_y),
                int(self.rotation_radius),
                2  # Outline only
            )

    def get_platforms(self):
        """Return sprite group of current platforms"""
        # CRITICAL: Only return platforms if arena is active
        if not self.active:
            return pygame.sprite.Group()  # Return empty group if inactive
        return self.platforms

    def deactivate(self):
        """Deactivate arena and clear platforms"""
        self.active = False
        self.platforms.empty()
        self.rotating_platforms.clear()
        self.single_platform = None
