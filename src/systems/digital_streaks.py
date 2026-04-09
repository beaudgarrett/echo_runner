# src/systems/digital_streaks.py
import pygame
import random
import math


class DigitalStreak:
    """Tron-like glitchy digital streak for level 2 atmosphere"""

    def __init__(self, world_width, screen_height):
        # Random starting position
        self.world_width = world_width
        self.screen_height = screen_height

        # Determine streak direction
        self.direction = random.choice(["horizontal", "vertical", "diagonal"])

        if self.direction == "horizontal":
            # Horizontal streaks move left or right
            self.x = random.uniform(0, world_width)
            self.y = random.uniform(0, screen_height)
            self.vel_x = random.choice([-1, 1]) * random.uniform(300, 600)
            self.vel_y = 0
            self.length = random.randint(100, 300)
            self.thickness = random.randint(1, 3)
        elif self.direction == "vertical":
            # Vertical streaks move up or down
            self.x = random.uniform(0, world_width)
            self.y = random.uniform(-100, screen_height + 100)
            self.vel_x = 0
            self.vel_y = random.choice([-1, 1]) * random.uniform(200, 400)
            self.length = random.randint(80, 200)
            self.thickness = random.randint(1, 2)
        else:  # diagonal
            # Diagonal streaks
            self.x = random.uniform(0, world_width)
            self.y = random.uniform(-100, screen_height + 100)
            direction_x = random.choice([-1, 1])
            direction_y = random.choice([-1, 1])
            speed = random.uniform(250, 500)
            self.vel_x = direction_x * speed
            self.vel_y = direction_y * speed
            self.length = random.randint(60, 150)
            self.thickness = random.randint(1, 2)

        # Color - tron-like neon colors
        self.color = random.choice([
            (0, 255, 255),     # Cyan (primary tron color)
            (255, 50, 255),    # Hot pink
            (0, 200, 255),     # Light blue
            (255, 255, 50),    # Yellow
            (100, 255, 255),   # Pale cyan
        ])

        # Visual properties
        self.alpha = random.randint(40, 120)  # Very faint
        self.lifetime = random.uniform(2.0, 4.0)
        self.age = 0.0

        # Glitch effect properties
        self.glitch_timer = 0.0
        self.glitch_interval = random.uniform(0.1, 0.3)
        self.is_glitching = False
        self.segments = []  # For broken/glitchy appearance
        self.create_segments()

    def create_segments(self):
        """Create segmented appearance for glitch effect"""
        num_segments = random.randint(3, 8)
        segment_length = self.length / num_segments

        for i in range(num_segments):
            # Some segments might be missing (glitch effect)
            if random.random() > 0.3:  # 70% chance to show segment
                offset = i * segment_length
                length = segment_length * random.uniform(0.7, 1.3)
                self.segments.append({
                    'offset': offset,
                    'length': length,
                    'active': True
                })

    def update(self, dt):
        """Update streak position and glitch state"""
        self.age += dt

        # Move the streak
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        # Glitch effect - randomly flicker segments
        self.glitch_timer += dt
        if self.glitch_timer >= self.glitch_interval:
            self.glitch_timer = 0.0
            self.is_glitching = not self.is_glitching

            # Randomly toggle some segments
            for segment in self.segments:
                if random.random() > 0.7:
                    segment['active'] = not segment['active']

    def is_dead(self, camera_x, screen_width):
        """Check if streak is off-screen and should be removed"""
        # Check if too old
        if self.age >= self.lifetime:
            return True

        # Check if off screen
        if self.direction == "horizontal":
            if self.vel_x > 0:  # Moving right
                return self.x - camera_x > screen_width + 200
            else:  # Moving left
                return self.x - camera_x < -200
        elif self.direction == "vertical":
            return self.y < -300 or self.y > self.screen_height + 300
        else:  # diagonal
            off_x = self.x - camera_x < -300 or self.x - camera_x > screen_width + 300
            off_y = self.y < -300 or self.y > self.screen_height + 300
            return off_x or off_y

    def draw(self, screen, camera_x):
        """Draw the digital streak with glitch effects"""
        # Calculate screen position
        screen_x = self.x - camera_x
        screen_y = self.y

        # Create surface for the streak
        if self.direction == "horizontal":
            for segment in self.segments:
                if segment['active']:
                    start_x = screen_x + segment['offset']
                    end_x = start_x + segment['length']
                    start_pos = (int(start_x), int(screen_y))
                    end_pos = (int(end_x), int(screen_y))

                    # Draw main line
                    if 0 <= screen_y <= self.screen_height:
                        pygame.draw.line(screen, self.color, start_pos, end_pos, self.thickness)

                        # Draw glow effect
                        glow_surf = pygame.Surface((int(segment['length']), self.thickness * 4), pygame.SRCALPHA)
                        glow_color = (*self.color, self.alpha // 2)
                        pygame.draw.line(glow_surf, glow_color,
                                       (0, self.thickness * 2),
                                       (int(segment['length']), self.thickness * 2),
                                       self.thickness * 2)
                        screen.blit(glow_surf, (int(start_x), int(screen_y - self.thickness * 2)))

        elif self.direction == "vertical":
            for segment in self.segments:
                if segment['active']:
                    start_y = screen_y + segment['offset']
                    end_y = start_y + segment['length']
                    start_pos = (int(screen_x), int(start_y))
                    end_pos = (int(screen_x), int(end_y))

                    # Draw main line
                    pygame.draw.line(screen, self.color, start_pos, end_pos, self.thickness)

                    # Draw glow
                    glow_surf = pygame.Surface((self.thickness * 4, int(segment['length'])), pygame.SRCALPHA)
                    glow_color = (*self.color, self.alpha // 2)
                    pygame.draw.line(glow_surf, glow_color,
                                   (self.thickness * 2, 0),
                                   (self.thickness * 2, int(segment['length'])),
                                   self.thickness * 2)
                    screen.blit(glow_surf, (int(screen_x - self.thickness * 2), int(start_y)))

        else:  # diagonal
            angle = math.atan2(self.vel_y, self.vel_x)
            for segment in self.segments:
                if segment['active']:
                    offset_x = math.cos(angle) * segment['offset']
                    offset_y = math.sin(angle) * segment['offset']
                    length_x = math.cos(angle) * segment['length']
                    length_y = math.sin(angle) * segment['length']

                    start_pos = (int(screen_x + offset_x), int(screen_y + offset_y))
                    end_pos = (int(screen_x + offset_x + length_x), int(screen_y + offset_y + length_y))

                    # Draw main line
                    pygame.draw.line(screen, self.color, start_pos, end_pos, self.thickness)


class DigitalStreakSystem:
    """Manager for level 2 tron-like digital streaks"""

    def __init__(self, world_width, screen_height=720):
        self.world_width = world_width
        self.screen_height = screen_height
        self.streaks = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.5  # Spawn a streak every 0.5 seconds
        self.max_streaks = 15  # Maximum active streaks at once

    def update(self, dt, camera_x, screen_width):
        """Update all streaks and spawn new ones"""
        # Update existing streaks
        for streak in self.streaks:
            streak.update(dt)

        # Remove dead streaks
        self.streaks = [s for s in self.streaks if not s.is_dead(camera_x, screen_width)]

        # Spawn new streaks
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.streaks) < self.max_streaks:
            self.spawn_timer = 0.0
            # Spawn near camera view
            self.streaks.append(DigitalStreak(self.world_width, self.screen_height))

    def draw(self, screen, camera_x):
        """Draw all active streaks"""
        for streak in self.streaks:
            streak.draw(screen, camera_x)
