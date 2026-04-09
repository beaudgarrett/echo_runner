# src/entities/item.py
import pygame
import os
import math
from src.core.utils import load_image, get_resource_path


class EnergyDrink(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        img_path = "assets/items/Monster.png"
        if not os.path.exists(get_resource_path(img_path)):
            img_path = "assets/items/terminal.png"  # fallback

        self.image = load_image(img_path)
        max_size = 48
        if self.image.get_width() > max_size or self.image.get_height() > max_size:
            self.image = pygame.transform.scale(self.image, (max_size, max_size))

        self.start_y = pos[1]
        self.rect = self.image.get_rect(center=pos)

        self.hover_amplitude = 5
        self.hover_speed = 2
        self.t = 0
        self.item_type = "energy"

    def update(self, dt):
        self.t += dt
        offset = math.sin(self.t * self.hover_speed) * self.hover_amplitude
        self.rect.centery = self.start_y + offset


class SpeedBoost(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Create a speed boost icon (lightning bolt)
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Draw lightning bolt
        points = [
            (20, 5), (10, 20), (18, 20), 
            (10, 35), (30, 15), (22, 15)
        ]
        pygame.draw.polygon(self.image, (255, 255, 0), points)
        pygame.draw.polygon(self.image, (255, 200, 0), points, 2)
        
        # Add glow effect
        glow = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 0, 50), (25, 25), 25)
        self.image.blit(glow, (-5, -5))
        
        self.start_y = pos[1]
        self.rect = self.image.get_rect(center=pos)
        self.hover_amplitude = 7
        self.hover_speed = 3
        self.t = 0
        self.item_type = "speed"
        
    def update(self, dt):
        self.t += dt
        offset = math.sin(self.t * self.hover_speed) * self.hover_amplitude
        self.rect.centery = self.start_y + offset


class LifeRestore(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Create a heart icon
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Draw heart shape
        pygame.draw.circle(self.image, (255, 50, 100), (12, 15), 8)
        pygame.draw.circle(self.image, (255, 50, 100), (28, 15), 8)
        points = [(5, 18), (20, 35), (35, 18)]
        pygame.draw.polygon(self.image, (255, 50, 100), points)
        
        # Add pulse glow
        glow = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 100, 150, 40), (25, 25), 22)
        self.image.blit(glow, (-5, -5))
        
        self.start_y = pos[1]
        self.rect = self.image.get_rect(center=pos)
        self.base_image = self.image.copy()
        self.hover_amplitude = 3
        self.hover_speed = 4
        self.t = 0
        self.item_type = "life"
        self.pulse_scale = 1.0
        
    def update(self, dt):
        # Pulse and hover
        self.t += dt
        
        # Hover movement
        offset = math.sin(self.t * self.hover_speed) * self.hover_amplitude
        
        # Pulse effect
        self.pulse_scale = 1.0 + math.sin(self.t * 4) * 0.1
        new_size = (int(40 * self.pulse_scale), int(40 * self.pulse_scale))
        self.image = pygame.transform.scale(self.base_image, new_size)
        
        # Update position
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        self.rect.centery = self.start_y + offset


class EasterEgg(pygame.sprite.Sprite):
    """Hidden collectible secret easter egg - one per level"""
    def __init__(self, pos):
        super().__init__()

        # Create a glowing golden egg icon
        self.image = pygame.Surface((45, 50), pygame.SRCALPHA)

        # Draw egg shape
        # Outer glow
        for i in range(4, 0, -1):
            alpha = 30 + (i * 10)
            pygame.draw.ellipse(self.image, (255, 215, 0, alpha),
                              (10-i*2, 5-i*2, 25+i*4, 40+i*4))

        # Main egg body (golden gradient effect)
        pygame.draw.ellipse(self.image, (255, 215, 0), (10, 5, 25, 40))
        pygame.draw.ellipse(self.image, (255, 235, 100), (12, 8, 21, 35))

        # Highlight shine
        pygame.draw.ellipse(self.image, (255, 255, 200, 180), (14, 10, 10, 12))

        # Add sparkle particles around it
        sparkle_positions = [(5, 15), (40, 15), (22, 2), (8, 38), (37, 38)]
        for x, y in sparkle_positions:
            pygame.draw.circle(self.image, (255, 255, 100, 200), (x, y), 2)

        self.start_y = pos[1]
        self.rect = self.image.get_rect(center=pos)
        self.base_image = self.image.copy()
        self.hover_amplitude = 8
        self.hover_speed = 1.5
        self.t = 0
        self.item_type = "easter_egg"
        self.rotation = 0

    def update(self, dt):
        self.t += dt

        # Hover movement
        offset = math.sin(self.t * self.hover_speed) * self.hover_amplitude

        # Gentle rotation
        self.rotation += dt * 30  # 30 degrees per second
        rotated = pygame.transform.rotate(self.base_image, self.rotation)

        # Update image and position
        old_center = self.rect.center
        self.image = rotated
        self.rect = self.image.get_rect(center=old_center)
        self.rect.centery = self.start_y + offset
