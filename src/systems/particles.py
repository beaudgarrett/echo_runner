# src/systems/particles.py
"""
Enhanced Visual Feedback - Particle Burst System
Creates vibrant data fragment explosions during gameplay events
"""
import pygame
import random
import math


class ParticleBurst:
    """Manages short-lived particle bursts for visual feedback"""

    def __init__(self):
        self.particles = []
        self.level_decay = 1.0  # Decreases lifetime by 10% per level

    def set_level(self, level):
        """Adjust particle decay based on current level (simulation decay)"""
        self.level_decay = 1.0 - (level * 0.1)
        if self.level_decay < 0.5:
            self.level_decay = 0.5  # Minimum 50% lifetime

    def spawn_burst(self, pos, event_type, count=None):
        """
        Spawn a particle burst at position

        Args:
            pos: (x, y) position
            event_type: 'energy_drink', 'drone_kill', 'player_damage', 'stability_gain', 'platform_fade'
            count: Number of particles (default varies by type)
        """
        # Color mapping based on event type
        color_map = {
            'energy_drink': (0, 255, 255),      # Cyan
            'drone_kill': (255, 0, 255),        # Magenta
            'player_damage': (255, 50, 50),     # Red
            'stability_gain': (180, 220, 255),  # Pale Blue-White
            'platform_fade': (255, 150, 0),     # Orange-Red
        }

        # Default particle counts
        count_map = {
            'energy_drink': 20,
            'drone_kill': 25,
            'player_damage': 30,
            'stability_gain': 15,
            'platform_fade': 18,
        }

        base_color = color_map.get(event_type, (255, 255, 255))
        particle_count = count if count else count_map.get(event_type, 20)

        for _ in range(particle_count):
            # Random angle and speed
            angle = random.random() * math.pi * 2
            speed = random.uniform(100, 300)

            # Size variation
            size = random.randint(2, 5)

            # Lifetime with level decay
            lifetime = random.uniform(0.5, 1.2) * self.level_decay

            # Color variation
            color = (
                min(255, base_color[0] + random.randint(-20, 20)),
                min(255, base_color[1] + random.randint(-20, 20)),
                min(255, base_color[2] + random.randint(-20, 20))
            )

            particle = {
                'pos': list(pos),
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'rotation': random.random() * 360,
                'rotation_speed': random.uniform(-360, 360)
            }

            self.particles.append(particle)

    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            # Update position
            particle['pos'][0] += particle['vel'][0] * dt
            particle['pos'][1] += particle['vel'][1] * dt

            # Apply gravity/drag
            particle['vel'][1] += 150 * dt  # Slight downward pull
            particle['vel'][0] *= 0.98  # Horizontal drag
            particle['vel'][1] *= 0.98  # Vertical drag

            # Update rotation
            particle['rotation'] += particle['rotation_speed'] * dt

            # Decrease lifetime
            particle['lifetime'] -= dt

            # Remove dead particles
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        """Draw all particles with glow effect"""
        for particle in self.particles:
            # Calculate fade alpha
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            alpha = max(0, min(255, alpha))  # Clamp to valid range

            pos = (int(particle['pos'][0]), int(particle['pos'][1]))
            size = particle['size']
            color = particle['color']

            # Ensure color values are valid integers in range 0-255
            color = (
                max(0, min(255, int(color[0]))),
                max(0, min(255, int(color[1]))),
                max(0, min(255, int(color[2])))
            )

            # Create surface for particle with alpha
            particle_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)

            # Draw glow (outer halo)
            glow_alpha = max(0, min(255, alpha // 3))
            glow_color = (color[0], color[1], color[2], glow_alpha)
            pygame.draw.circle(particle_surf, glow_color, (size * 3 // 2, size * 3 // 2), size * 2)

            # Draw core particle
            core_color = (color[0], color[1], color[2], alpha)
            pygame.draw.rect(particle_surf, core_color, (size, size, size, size))

            # Blit to screen
            screen.blit(particle_surf, (pos[0] - size, pos[1] - size), special_flags=pygame.BLEND_ADD)

    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class EliminatedText:
    """Displays 'ELIMINATED' text with screen flash when drone is killed"""

    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 0.5
        self.flash_duration = 0.15
        self.jitter_amount = 4
        self.text = "ELIMINATED"
        self.font = None
        self.hue_cycle = 0.0

    def trigger(self, font):
        """Activate the ELIMINATED text"""
        self.active = True
        self.timer = 0.0
        self.font = font
        self.hue_cycle = 0.0

    def update(self, dt):
        """Update timer and effects"""
        if self.active:
            self.timer += dt
            self.hue_cycle += dt * 10  # Fast color cycling

            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen):
        """Draw ELIMINATED text with LOCALIZED glow effects (no full-screen overlay)"""
        if not self.active or not self.font:
            return

        # Calculate fade
        alpha = int(255 * (1.0 - (self.timer / self.duration)))

        # FIXED: Removed full-screen flash overlay that was causing phantom platforms
        # Instead, we'll use a localized glow effect around the text only

        # Color cycling (red -> magenta -> white)
        cycle_pos = (self.hue_cycle % 3) / 3.0
        if cycle_pos < 0.33:
            color = (255, int(50 + 205 * (cycle_pos * 3)), 50)
        elif cycle_pos < 0.66:
            color = (255, int(255 - 205 * ((cycle_pos - 0.33) * 3)), 255)
        else:
            color = (255, 255, 255)

        # Horizontal jitter
        jitter_x = random.randint(-self.jitter_amount, self.jitter_amount)

        # Center position with jitter
        width, height = screen.get_size()
        base_x = width // 2 + jitter_x
        base_y = height // 2

        # CRT flicker effect (sine wave alpha modulation)
        flicker = abs(math.sin(self.timer * 30))
        final_alpha = int(alpha * (0.7 + 0.3 * flicker))

        # LOCALIZED GLOW EFFECT: Draw multiple offset copies with decreasing alpha
        # This creates a glow around the text without affecting the entire screen
        if self.timer < self.flash_duration:
            # Initial flash intensity (brightest in first frames)
            flash_intensity = 1.0 - (self.timer / self.flash_duration)

            # Draw outer glow layers (white with decreasing alpha)
            glow_offsets = [(0, 0, 1.0), (-2, -2, 0.6), (2, -2, 0.6), (-2, 2, 0.6), (2, 2, 0.6),
                           (-4, 0, 0.4), (4, 0, 0.4), (0, -4, 0.4), (0, 4, 0.4)]

            for dx, dy, intensity in glow_offsets:
                glow_surf = self.font.render(self.text, True, (255, 255, 255))
                glow_alpha = int(final_alpha * intensity * flash_intensity * 0.8)
                glow_surf.set_alpha(glow_alpha)
                glow_pos = (base_x - glow_surf.get_width() // 2 + dx,
                           base_y - glow_surf.get_height() // 2 + dy)
                screen.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ADD)

        # Draw main text with color
        text_surf = self.font.render(self.text, True, color)
        text_surf.set_alpha(final_alpha)
        pos = (base_x - text_surf.get_width() // 2,
               base_y - text_surf.get_height() // 2)
        screen.blit(text_surf, pos, special_flags=pygame.BLEND_ADD)


class ComboCounter:
    """Tracks and displays kill combo with momentum bonuses"""

    def __init__(self):
        self.combo = 0
        self.timer = 0.0
        self.combo_window = 2.0  # 2 seconds to continue combo
        self.active = False
        self.font = None
        self.jitter = 0
        self.hue_cycle = 0.0
        self.shatter_particles = []

    def add_kill(self, font):
        """Increment combo on kill"""
        self.combo += 1
        self.timer = 0.0
        self.active = True
        self.font = font

        # Check for dash reward (every 5 kills)
        dash_awarded = False
        if self.combo % 5 == 0 and self.combo > 0:
            dash_awarded = True

        return dash_awarded

    def reset(self, pos):
        """Reset combo and create shatter effect"""
        if self.combo > 1:  # Only shatter if combo was significant
            # Create shatter particles
            for _ in range(8 + self.combo):
                angle = random.random() * math.pi * 2
                speed = random.uniform(100, 250)
                self.shatter_particles.append({
                    'pos': list(pos),
                    'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                    'life': 0.3,
                    'color': (255, 0, 255) if random.random() > 0.5 else (0, 255, 255)
                })

        self.combo = 0
        self.active = False

    def update(self, dt, player_pos):
        """Update combo timer and effects"""
        if self.active:
            self.timer += dt
            self.hue_cycle += dt * 8
            self.jitter = random.randint(-2, 2)

            # Reset if window expires
            if self.timer >= self.combo_window:
                self.reset(player_pos)

        # Update shatter particles
        for particle in self.shatter_particles[:]:
            particle['pos'][0] += particle['vel'][0] * dt
            particle['pos'][1] += particle['vel'][1] * dt
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.shatter_particles.remove(particle)

    def draw(self, screen):
        """Draw combo counter with glitch effects"""
        if not self.active or not self.font or self.combo < 2:
            return

        # Color oscillation (magenta <-> cyan)
        cycle_pos = (self.hue_cycle % 2) / 2.0
        if cycle_pos < 0.5:
            color = (255, int(255 * cycle_pos * 2), 255)
        else:
            color = (int(255 * (1 - (cycle_pos - 0.5) * 2)), 255, 255)

        # Render combo text
        text = f"×{self.combo}"
        text_surf = self.font.render(text, True, color)

        # Flicker alpha
        alpha = int(200 + 55 * abs(math.sin(self.hue_cycle * 5)))
        text_surf.set_alpha(alpha)

        # Position (top-right with jitter)
        width = screen.get_size()[0]
        pos = (width - 150 + self.jitter, 20 + self.jitter)

        # Additive blending for glow
        screen.blit(text_surf, pos, special_flags=pygame.BLEND_ADD)

        # Draw shatter particles
        for particle in self.shatter_particles:
            alpha = int(255 * (particle['life'] / 0.3))
            particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            particle_surf.fill((*particle['color'], alpha))
            screen.blit(particle_surf,
                       (int(particle['pos'][0]), int(particle['pos'][1])),
                       special_flags=pygame.BLEND_ADD)
