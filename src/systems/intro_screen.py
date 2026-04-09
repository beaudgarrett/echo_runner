# src/systems/intro_screen.py
import pygame
import random
import math


class VortexParticle:
    """Swirling vortex particle for the intro background"""

    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.angle = random.uniform(0, math.pi * 2)
        self.radius = radius
        self.angular_speed = random.uniform(1.5, 3.0)
        self.color = random.choice([
            (255, 50, 255),   # Hot pink
            (50, 255, 255),   # Cyan
            (255, 255, 50),   # Yellow
            (150, 50, 255),   # Purple
            (255, 150, 50)    # Orange
        ])
        self.size = random.randint(2, 6)
        self.alpha = random.randint(100, 255)

    def update(self, dt):
        self.angle += self.angular_speed * dt
        # Spiral inward slowly
        self.radius = max(10, self.radius - 20 * dt)

    def get_position(self):
        x = self.center_x + math.cos(self.angle) * self.radius
        y = self.center_y + math.sin(self.angle) * self.radius
        return (int(x), int(y))


class GlitchParticle:
    """Falling glitch/reality fragment"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = random.uniform(100, 300)
        self.vel_x = random.uniform(-50, 50)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-180, 180)
        self.size = random.randint(4, 12)
        self.color = random.choice([
            (255, 50, 255),
            (50, 255, 255),
            (255, 100, 255),
            (100, 255, 255)
        ])
        self.lifetime = random.uniform(3.0, 5.0)
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.y += self.vel_y * dt
        self.x += self.vel_x * dt
        self.rotation += self.rotation_speed * dt

    def is_dead(self):
        return self.age >= self.lifetime or self.y > 800

    def draw(self, screen):
        alpha = int(255 * (1.0 - self.age / self.lifetime))
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Draw with RGB color only
        pygame.draw.rect(surf, self.color, (0, 0, self.size, self.size))
        # Apply alpha to the entire surface
        surf.set_alpha(alpha)

        # Rotate
        rotated = pygame.transform.rotate(surf, self.rotation)
        screen.blit(rotated, (int(self.x - rotated.get_width() / 2),
                             int(self.y - rotated.get_height() / 2)))


class IntroScreen:
    """Epic intro screen with vortexes, particles, and running player"""

    def __init__(self):
        self.font_title = pygame.font.Font(None, 100)
        self.font_subtitle = pygame.font.Font(None, 48)
        self.font_prompt = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 20)

        self.timer = 0.0
        self.active = True

        # Vortex particles (multiple vortexes)
        self.vortexes = []
        self.spawn_vortexes()

        # Glitch particles
        self.glitch_particles = []
        self.glitch_spawn_timer = 0.0

        # Player silhouette animation
        self.player_anim_timer = 0.0
        self.player_x = -100  # Start off-screen left
        self.player_run_speed = 200  # Pixels per second

        # Pulsing glow effect
        self.glow_timer = 0.0

    def spawn_vortexes(self):
        """Create multiple vortex centers"""
        # Create 3 vortexes at different positions
        positions = [
            (320, 200),   # Top left
            (960, 250),   # Top right
            (640, 500),   # Bottom center
        ]

        for center_x, center_y in positions:
            # Each vortex has multiple particles
            for _ in range(30):
                radius = random.uniform(50, 300)
                self.vortexes.append(VortexParticle(center_x, center_y, radius))

    def update(self, dt):
        self.timer += dt
        self.glow_timer += dt

        # Update vortex particles
        for vortex in self.vortexes:
            vortex.update(dt)

            # Respawn particles that spiraled too far in
            if vortex.radius < 20:
                vortex.radius = random.uniform(200, 350)

        # Spawn glitch particles
        self.glitch_spawn_timer += dt
        if self.glitch_spawn_timer >= 0.1:
            self.glitch_spawn_timer = 0.0
            x = random.uniform(0, 1280)
            y = random.uniform(-50, -10)
            self.glitch_particles.append(GlitchParticle(x, y))

        # Update glitch particles
        self.glitch_particles = [p for p in self.glitch_particles if not p.is_dead()]
        for particle in self.glitch_particles:
            particle.update(dt)

        # Animate player running across screen
        self.player_anim_timer += dt
        self.player_x += self.player_run_speed * dt
        # Loop player back around
        if self.player_x > 1380:
            self.player_x = -100

    def draw(self, screen):
        # Dark background with gradient
        for y in range(0, 720, 2):
            darkness = int(30 + (y / 720) * 20)
            pygame.draw.line(screen, (darkness, 0, darkness), (0, y), (1280, y))

        # Draw vortex particles (create spiral effect)
        for vortex in self.vortexes:
            pos = vortex.get_position()
            # Draw with glow
            for i in range(3):
                glow_size = vortex.size + (3 - i) * 2
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                glow_alpha = vortex.alpha // (i + 1)
                pygame.draw.circle(glow_surf, (*vortex.color, glow_alpha),
                                  (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (pos[0] - glow_size, pos[1] - glow_size))

        # Draw glitch particles
        for particle in self.glitch_particles:
            particle.draw(screen)

        # Draw running player silhouette
        self.draw_running_player(screen)

        # Pulsing glow intensity
        pulse = abs(math.sin(self.glow_timer * 2))

        # Title text with neon glow
        title_text = "ECHO RUNNER"
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(640, 280))

        # Draw multiple glowing layers
        for i in range(5):
            glow_intensity = int(150 * pulse * (1 - i * 0.15))
            glow_color = (0, 255, 255) if i % 2 == 0 else (255, 50, 255)
            glow_surf = self.font_title.render(title_text, True, (*glow_color, 0))
            glow_rect = glow_surf.get_rect(center=(640 + random.randint(-2, 2),
                                                    280 + random.randint(-2, 2)))
            glow_surf.set_alpha(glow_intensity)
            screen.blit(glow_surf, glow_rect)

        # Main title
        screen.blit(title_surf, title_rect)

        # Subtitle
        subtitle_text = "By Beau Garrett"
        subtitle_surf = self.font_subtitle.render(subtitle_text, True, (150, 255, 255))
        subtitle_rect = subtitle_surf.get_rect(center=(640, 360))

        # Subtitle glow
        subtitle_glow = self.font_subtitle.render(subtitle_text, True, (255, 50, 255))
        subtitle_glow.set_alpha(int(100 * pulse))
        screen.blit(subtitle_glow, subtitle_rect)
        screen.blit(subtitle_surf, subtitle_rect)

        # Prompt to start (blinking)
        blink = int(self.timer * 2) % 2
        if blink == 0:
            prompt_text = "PRESS ANY KEY TO BEGIN"
            prompt_surf = self.font_prompt.render(prompt_text, True, (255, 255, 50))
            prompt_rect = prompt_surf.get_rect(center=(640, 500))
            screen.blit(prompt_surf, prompt_rect)

        # Scanline effect
        for y in range(0, 720, 4):
            pygame.draw.line(screen, (0, 0, 0, 30), (0, y), (1280, y), 1)

        # Secret code in bottom right corner
        secret_text = "1437"
        secret_surf = self.font_tiny.render(secret_text, True, (80, 80, 100))
        secret_rect = secret_surf.get_rect(bottomright=(1270, 710))
        screen.blit(secret_surf, secret_rect)

    def draw_running_player(self, screen):
        """Draw a simplified running player silhouette"""
        # Create player silhouette
        player_width = 48
        player_height = 48

        # Animated running (simple bob and leg movement)
        bob = abs(math.sin(self.player_anim_timer * 10)) * 5

        # Player body (rectangle with glow)
        player_y = 600 - bob

        # Draw glowing silhouette
        for i in range(3):
            glow_size = 4 - i
            glow_color = (0, 255, 255) if i == 0 else (255, 50, 255)
            glow_rect = pygame.Rect(self.player_x - glow_size, player_y - glow_size,
                                     player_width + glow_size * 2, player_height + glow_size * 2)
            glow_alpha = 100 - i * 30
            glow_surf = pygame.Surface((player_width + glow_size * 4,
                                        player_height + glow_size * 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*glow_color, glow_alpha),
                           (glow_size * 2, glow_size * 2, player_width, player_height),
                           border_radius=5)
            screen.blit(glow_surf, (self.player_x - glow_size * 2, player_y - glow_size * 2))

        # Main player silhouette
        pygame.draw.rect(screen, (255, 255, 255),
                        (self.player_x, player_y, player_width, player_height),
                        border_radius=5)

        # Trail effect
        trail_alpha = 100
        for trail_offset in range(1, 4):
            trail_x = self.player_x - trail_offset * 15
            trail_surf = pygame.Surface((player_width, player_height), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, (0, 255, 255, trail_alpha // trail_offset),
                           (0, 0, player_width, player_height), border_radius=5)
            screen.blit(trail_surf, (trail_x, player_y))
