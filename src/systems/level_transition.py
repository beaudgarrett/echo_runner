# src/systems/level_transition.py
import pygame
import math
import random
from settings import WIDTH, HEIGHT


class VortexParticle:
    """Particle for the vortex portal effect"""

    def __init__(self, angle, distance, speed):
        self.angle = angle
        self.distance = distance
        self.speed = speed
        self.size = random.randint(2, 6)
        self.color = random.choice([
            (0, 255, 255),     # Cyan
            (255, 50, 255),    # Hot pink
            (255, 255, 50),    # Yellow
            (150, 50, 255),    # Purple
        ])
        self.alpha = random.randint(150, 255)

    def update(self, dt):
        # Spiral inward
        self.distance -= self.speed * dt
        self.angle += 3.0 * dt  # Rotate while moving inward

    def get_position(self, center_x, center_y):
        x = center_x + math.cos(self.angle) * self.distance
        y = center_y + math.sin(self.angle) * self.distance
        return (int(x), int(y))

    def is_dead(self):
        return self.distance < 10


class LevelTransition:
    """Epic vortex portal transition between levels"""

    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 3.0  # 3 second transition
        self.target_level = 1
        self.level_names = {
            1: "FIRST SIMULATION LAYER",
            2: "CORRUPT SECTOR",
            3: "ARCHON CORE"
        }

        # Vortex particles
        self.particles = []
        self.particle_spawn_timer = 0.0
        self.particle_spawn_interval = 0.02  # Spawn very frequently

        # Visual effects
        self.pulse_timer = 0.0
        self.rotation = 0.0

        # Fonts
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

    def start(self, level_num):
        """Begin the transition to a new level"""
        self.active = True
        self.timer = 0.0
        self.target_level = level_num
        self.particles = []
        print(f"Level transition started - going to level {level_num}")

    def is_complete(self):
        """Check if transition animation is done"""
        return self.timer >= self.duration

    def update(self, dt):
        """Update transition animation"""
        if not self.active:
            return

        self.timer += dt
        self.pulse_timer += dt
        self.rotation += dt * 180  # Rotate 180 degrees per second

        # Spawn vortex particles
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= self.particle_spawn_interval:
            self.particle_spawn_timer = 0.0
            # Spawn particles in a circle at the edge
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(350, 400)
                speed = random.uniform(150, 250)
                self.particles.append(VortexParticle(angle, distance, speed))

        # Update particles
        for particle in self.particles:
            particle.update(dt)

        # Remove dead particles
        self.particles = [p for p in self.particles if not p.is_dead()]

        # End transition when complete
        if self.is_complete():
            self.active = False

    def draw(self, screen):
        """Draw the vortex portal transition"""
        if not self.active:
            return

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        # Calculate fade phases
        fade_in_duration = 0.5
        fade_out_duration = 0.5
        fade_alpha = 255

        if self.timer < fade_in_duration:
            # Fade in
            fade_alpha = int((self.timer / fade_in_duration) * 255)
        elif self.timer > self.duration - fade_out_duration:
            # Fade out
            time_left = self.duration - self.timer
            fade_alpha = int((time_left / fade_out_duration) * 255)

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, min(220, fade_alpha)))
        screen.blit(overlay, (0, 0))

        # Draw vortex particles
        for particle in self.particles:
            pos = particle.get_position(center_x, center_y)
            # Draw particle with glow
            for i in range(3):
                glow_size = particle.size + (3 - i) * 2
                glow_alpha = min(255, particle.alpha // (i + 1))
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*particle.color, glow_alpha),
                                 (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (pos[0] - glow_size, pos[1] - glow_size))

        # Draw portal rings
        pulse = abs(math.sin(self.pulse_timer * 3))
        for ring_idx in range(5):
            ring_radius = 50 + ring_idx * 40 + int(pulse * 20)
            ring_color = [(0, 255, 255), (255, 50, 255), (0, 255, 255),
                         (255, 50, 255), (0, 255, 255)][ring_idx]
            ring_alpha = int((1.0 - ring_idx * 0.15) * 150)

            # Create ring surface
            ring_size = ring_radius * 2 + 10
            ring_surf = pygame.Surface((ring_size, ring_size), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*ring_color, ring_alpha),
                             (ring_size // 2, ring_size // 2), ring_radius, 3)

            # Rotate ring
            rotated = pygame.transform.rotate(ring_surf, self.rotation + ring_idx * 30)
            rotated_rect = rotated.get_rect(center=(center_x, center_y))
            screen.blit(rotated, rotated_rect)

        # Draw central glow
        glow_size = 100 + int(pulse * 30)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        for i in range(5):
            alpha = int((5 - i) * 15)
            size = glow_size - i * 15
            pygame.draw.circle(glow_surf, (255, 255, 255, alpha),
                             (glow_size, glow_size), size)
        screen.blit(glow_surf, (center_x - glow_size, center_y - glow_size))

        # Text appears in the middle phase
        text_alpha = 0
        mid_start = 0.8
        mid_end = 2.2

        if mid_start <= self.timer <= mid_end:
            # Calculate text alpha
            if self.timer < mid_start + 0.3:
                text_alpha = int(((self.timer - mid_start) / 0.3) * 255)
            elif self.timer > mid_end - 0.3:
                text_alpha = int(((mid_end - self.timer) / 0.3) * 255)
            else:
                text_alpha = 255

        if text_alpha > 0:
            # "WELCOME TO" text
            welcome_text = "WELCOME TO"
            welcome_surf = self.font_medium.render(welcome_text, True, (255, 255, 255))
            welcome_surf.set_alpha(text_alpha)
            welcome_rect = welcome_surf.get_rect(center=(center_x, center_y - 60))
            screen.blit(welcome_surf, welcome_rect)

            # Level name with glow
            level_name = self.level_names.get(self.target_level, f"LEVEL {self.target_level}")

            # Glowing level name
            glow_pulse = abs(math.sin(self.pulse_timer * 4))
            for i in range(3):
                glow_color = (0, 255, 255) if i % 2 == 0 else (255, 50, 255)
                glow_surf = self.font_large.render(level_name, True, glow_color)
                glow_alpha = int(text_alpha * 0.5 * glow_pulse * (1 - i * 0.2))
                glow_surf.set_alpha(glow_alpha)
                glow_rect = glow_surf.get_rect(center=(center_x + random.randint(-2, 2),
                                                        center_y + random.randint(-2, 2)))
                screen.blit(glow_surf, glow_rect)

            # Main level name
            level_surf = self.font_large.render(level_name, True, (255, 255, 255))
            level_surf.set_alpha(text_alpha)
            level_rect = level_surf.get_rect(center=(center_x, center_y))
            screen.blit(level_surf, level_rect)

            # Subtitle
            subtitle_text = "INITIALIZING..."
            subtitle_surf = self.font_small.render(subtitle_text, True, (150, 255, 255))
            subtitle_surf.set_alpha(int(text_alpha * 0.7))
            subtitle_rect = subtitle_surf.get_rect(center=(center_x, center_y + 60))
            screen.blit(subtitle_surf, subtitle_rect)

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)
