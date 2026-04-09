# src/entities/tutorial_drone.py
"""
Tutorial practice drone - doesn't harm player, respawns infinitely
"""
import pygame
from src.entities.enemy_drone import EnemyDrone


class TutorialDrone(EnemyDrone):
    """
    A practice drone for tutorial that:
    - Doesn't damage the player
    - Respawns after being eliminated
    - Shows instructional text above it
    """

    def __init__(self, pos, patrol_range=100, speed=75):
        super().__init__(pos, patrol_range, speed, detection_radius=0)

        # Tutorial-specific properties
        self.spawn_pos = pos
        self.respawn_delay = 2.0
        self.respawn_timer = 0.0
        self.is_tutorial_drone = True  # Flag for game.py to identify
        self.instruction_text = "JUMP ON ME TO TERMINATE"
        self.text_color = (0, 255, 255)
        self.text_alpha = 255
        self.text_pulse = 0.0

        # Don't chase player in tutorial
        self.detection_radius = 0

    def update(self, dt):
        """Update with respawn logic and forced patrol"""
        # If dead, count down respawn timer
        if self.state == "dead":
            # Don't call super().update() - handle death manually
            self.animate(dt)
            self.death_timer += dt
            self.explosion_radius += 500 * dt
            self.explosion_alpha -= 600 * dt
            self.respawn_timer += dt

            # Respawn after delay
            if self.respawn_timer >= self.respawn_delay:
                self.respawn()
            return

        # FORCE patrol behavior (ignore player for tutorial)
        self.patrol(dt)
        self.animate(dt)

        # Update text pulse
        self.text_pulse += dt * 3

    def respawn(self):
        """Respawn the practice drone"""
        self.state = "patrol"
        self.frames = self.animations["walk"]
        self.frame_index = 0
        self.animation_speed = 0.1
        self.rect.topleft = self.spawn_pos
        self.death_timer = 0
        self.respawn_timer = 0.0
        self.explosion_radius = 0
        self.explosion_alpha = 0
        print("Tutorial drone respawned - try again!")

    def draw_instruction(self, screen, camera_x):
        """Draw floating instruction text above drone"""
        if self.state == "dead":
            return

        # Pulse alpha for visibility
        import math
        alpha = int(200 + 55 * abs(math.sin(self.text_pulse)))

        # Create font (size 20)
        font = pygame.font.Font(None, 24)

        # Render text
        text_surf = font.render(self.instruction_text, True, self.text_color)
        text_surf.set_alpha(alpha)

        # Position above drone (floating)
        text_pos = (
            self.rect.centerx - camera_x - text_surf.get_width() // 2,
            self.rect.top - 30
        )

        # Draw with glow effect
        screen.blit(text_surf, text_pos, special_flags=pygame.BLEND_ADD)
