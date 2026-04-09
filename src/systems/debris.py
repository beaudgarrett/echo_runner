# src/systems/debris.py
import pygame
import random
import math


class DebrisShard:
    """A single falling debris shard (motherboard fragment, code chunk, etc.)"""

    def __init__(self, x, y, world_width):
        self.x = x
        self.y = y
        self.world_width = world_width

        # Physics
        self.vel_y = random.uniform(50, 150)  # Falling speed
        self.vel_x = random.uniform(-20, 20)  # Slight horizontal drift
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)

        # Visual properties
        self.size = random.randint(8, 20)
        self.lifetime = random.uniform(5.0, 10.0)  # How long it exists
        self.age = 0.0

        # Shard type
        shard_types = ["circuit", "code", "glitch"]
        self.type = random.choice(shard_types)

        # Create the shard image
        self.image = self.create_shard_image()
        self.alpha = 200

    def create_shard_image(self):
        """Create a visual representation of the shard"""
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

        if self.type == "circuit":
            # Green circuit board fragment
            # Main chip
            pygame.draw.rect(surf, (0, 180, 100), (2, 2, self.size - 4, self.size - 4))
            # Circuit lines
            for i in range(3):
                y_pos = 2 + i * (self.size // 4)
                pygame.draw.line(surf, (0, 255, 150), (0, y_pos), (self.size, y_pos), 1)
            # Tiny squares (components)
            pygame.draw.rect(surf, (255, 200, 0), (self.size // 4, self.size // 4, 3, 3))
            pygame.draw.rect(surf, (255, 200, 0), (self.size - self.size // 4 - 3, self.size - self.size // 4 - 3, 3, 3))

        elif self.type == "code":
            # Cyan code fragment
            font = pygame.font.Font(None, self.size)
            code_chars = ["0", "1", "}", "{", "/", "\\", "<", ">"]
            char = random.choice(code_chars)
            text = font.render(char, True, (0, 255, 255))
            surf.blit(text, (0, 0))

        elif self.type == "glitch":
            # Purple/magenta glitch pixel block
            for i in range(self.size // 2):
                for j in range(self.size // 2):
                    if random.random() > 0.5:
                        color = random.choice([(255, 0, 255), (255, 100, 255), (200, 0, 200)])
                        pygame.draw.rect(surf, color, (i * 2, j * 2, 2, 2))

        return surf

    def update(self, dt):
        """Update shard position and physics"""
        self.age += dt

        # Move shard
        self.y += self.vel_y * dt
        self.x += self.vel_x * dt

        # Rotate
        self.rotation += self.rotation_speed * dt

        # Fade out near end of lifetime
        if self.age > self.lifetime * 0.7:
            fade_progress = (self.age - self.lifetime * 0.7) / (self.lifetime * 0.3)
            self.alpha = int(200 * (1.0 - fade_progress))

        # Wrap horizontally if goes out of bounds
        if self.x < -self.size:
            self.x = self.world_width + self.size
        elif self.x > self.world_width + self.size:
            self.x = -self.size

    def is_dead(self):
        """Check if shard should be removed"""
        return self.age >= self.lifetime or self.y > 800

    def draw(self, screen, camera_x):
        """Draw the shard with rotation and camera offset"""
        # Create rotated image
        rotated = pygame.transform.rotate(self.image, self.rotation)
        rotated.set_alpha(self.alpha)

        # Calculate screen position
        screen_x = self.x - camera_x - rotated.get_width() // 2
        screen_y = self.y - rotated.get_height() // 2

        screen.blit(rotated, (screen_x, screen_y))


class DebrisSystem:
    """Manages falling debris particles for environmental atmosphere"""

    def __init__(self, world_width):
        self.world_width = world_width
        self.shards = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.5  # Spawn every 0.5 seconds
        self.max_shards = 20  # Maximum number of active shards

    def update(self, dt, camera_x, screen_width):
        """Update all debris shards"""
        # Spawn new shards near camera view
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.shards) < self.max_shards:
            self.spawn_timer = 0.0
            # Spawn above the visible area, near camera position
            spawn_x = camera_x + random.uniform(-100, screen_width + 100)
            spawn_y = random.uniform(-100, -20)
            self.shards.append(DebrisShard(spawn_x, spawn_y, self.world_width))

        # Update existing shards
        self.shards = [shard for shard in self.shards if not shard.is_dead()]

        for shard in self.shards:
            shard.update(dt)

    def draw(self, screen, camera_x):
        """Draw all debris shards"""
        for shard in self.shards:
            shard.draw(screen, camera_x)

    def set_intensity(self, level):
        """Adjust debris spawn rate based on game state (1-3)"""
        if level == 1:
            self.spawn_interval = 0.8
            self.max_shards = 15
        elif level == 2:
            self.spawn_interval = 0.5
            self.max_shards = 25
        elif level == 3:
            self.spawn_interval = 0.3  # More intense for boss level
            self.max_shards = 35
