# src/systems/architect_mode.py
import pygame
import math
import random


class ArchitectMode:
    """System Architect mode - you become ARCHON and float in a stormy void"""

    def __init__(self):
        self.active = False
        self.timer = 0.0

        # Architect (player as ARCHON) position and movement
        self.arch_pos = pygame.Vector2(640, 360)
        self.arch_vel = pygame.Vector2(0, 0)
        self.arch_speed = 200
        self.arch_rotation = 0.0

        # Create ARCHON visual
        self.create_archon_sprite()

        # Purple orb projectiles
        self.orbs = []
        self.shoot_cooldown = 0.0

        # Storm background
        self.lightning_bolts = []
        self.storm_particles = []
        self.storm_intensity = 0.0

        # Fun interactive elements
        self.energy_spheres = []  # Collectible spheres that boost your power
        self.power_level = 1.0
        self.spawn_sphere_timer = 0.0

        # Destructible targets system
        self.targets = []
        self.spawn_target_timer = 0.0
        self.score = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.max_combo = 0

        # Achievements
        self.achievements = {
            'first_target': False,
            'combo_10': False,
            'combo_50': False,
            'power_maxed': False,
            'score_1000': False,
            'score_5000': False
        }
        self.achievement_popup = None
        self.achievement_popup_timer = 0.0

        # Initialize storm
        self.spawn_initial_storm()

    def create_archon_sprite(self):
        """Create the ARCHON visual (same as boss)"""
        size = 120
        self.archon_image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Core hexagon
        center = size // 2
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = center + 40 * math.cos(angle)
            y = center + 40 * math.sin(angle)
            hex_points.append((x, y))

        # Draw glowing core
        for i in range(5):
            alpha = 255 - i * 40
            color = (255, 50 + i * 20, 255, alpha)
            scaled_points = []
            for px, py in hex_points:
                dx = px - center
                dy = py - center
                scale = 1 + i * 0.1
                scaled_points.append((center + dx * scale, center + dy * scale))
            pygame.draw.polygon(self.archon_image, color, scaled_points, 2)

        # Central eye
        pygame.draw.circle(self.archon_image, (255, 255, 255), (center, center), 15)
        pygame.draw.circle(self.archon_image, (255, 0, 255), (center, center), 10)
        pygame.draw.circle(self.archon_image, (0, 0, 0), (center, center), 5)

    def spawn_initial_storm(self):
        """Create initial storm particles"""
        for i in range(200):
            particle = {
                'pos': pygame.Vector2(
                    random.randint(0, 1280),
                    random.randint(0, 720)
                ),
                'vel': pygame.Vector2(
                    random.uniform(-50, 50),
                    random.uniform(-50, 50)
                ),
                'size': random.randint(1, 4),
                'color': random.choice([
                    (100, 100, 150),
                    (80, 80, 120),
                    (150, 150, 200),
                    (200, 150, 255)
                ])
            }
            self.storm_particles.append(particle)

    def start(self):
        """Start architect mode"""
        self.active = True
        self.timer = 0.0
        self.arch_pos = pygame.Vector2(640, 360)
        self.arch_vel = pygame.Vector2(0, 0)
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        print("=== SYSTEM ARCHITECT MODE ACTIVATED ===")
        print("You are now ARCHON, the system architect.")
        print("WASD to float, SPACE to shoot purple orbs")
        print("Destroy rotating targets to build combos and score points!")
        print("Collect cyan energy spheres to increase power!")
        print("Unlock achievements by reaching milestones!")

    def handle_input(self, keys):
        """Handle movement input"""
        # WASD movement
        move_x = 0
        move_y = 0

        if keys[pygame.K_w]:
            move_y = -1
        if keys[pygame.K_s]:
            move_y = 1
        if keys[pygame.K_a]:
            move_x = -1
        if keys[pygame.K_d]:
            move_x = 1

        # Normalize diagonal movement
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length

        self.arch_vel.x = move_x * self.arch_speed
        self.arch_vel.y = move_y * self.arch_speed

    def shoot_orb(self, mouse_pos):
        """Shoot a purple orb towards mouse position"""
        if self.shoot_cooldown <= 0:
            # Calculate angle to mouse
            dx = mouse_pos[0] - self.arch_pos.x
            dy = mouse_pos[1] - self.arch_pos.y
            angle = math.atan2(dy, dx)

            # Create orb
            orb = {
                'pos': pygame.Vector2(self.arch_pos.x, self.arch_pos.y),
                'vel': pygame.Vector2(
                    math.cos(angle) * 400 * self.power_level,
                    math.sin(angle) * 400 * self.power_level
                ),
                'lifetime': 3.0,
                'size': int(8 * self.power_level)
            }
            self.orbs.append(orb)

            # Reset cooldown (faster with more power)
            self.shoot_cooldown = max(0.1, 0.3 / self.power_level)

    def spawn_energy_sphere(self):
        """Spawn a collectible energy sphere"""
        sphere = {
            'pos': pygame.Vector2(
                random.randint(100, 1180),
                random.randint(100, 620)
            ),
            'pulse': random.uniform(0, math.pi * 2),
            'lifetime': 10.0
        }
        self.energy_spheres.append(sphere)

    def spawn_target(self):
        """Spawn a destructible target"""
        # Random type of target
        target_type = random.choice(['small', 'medium', 'large'])

        if target_type == 'small':
            health = 1
            size = 25
            points = 10
            color = (255, 50, 50)
        elif target_type == 'medium':
            health = 2
            size = 40
            points = 25
            color = (255, 150, 50)
        else:  # large
            health = 3
            size = 60
            points = 50
            color = (255, 255, 50)

        target = {
            'pos': pygame.Vector2(
                random.randint(100, 1180),
                random.randint(100, 620)
            ),
            'vel': pygame.Vector2(
                random.uniform(-30, 30),
                random.uniform(-30, 30)
            ),
            'health': health,
            'max_health': health,
            'size': size,
            'points': points,
            'color': color,
            'pulse': random.uniform(0, math.pi * 2),
            'rotation': random.uniform(0, 360)
        }
        self.targets.append(target)

    def check_achievement(self, achievement_id, message):
        """Check and unlock an achievement"""
        if not self.achievements[achievement_id]:
            self.achievements[achievement_id] = True
            self.achievement_popup = message
            self.achievement_popup_timer = 3.0
            print(f"ACHIEVEMENT UNLOCKED: {message}")

    def destroy_target(self, target):
        """Destroy a target and award points"""
        self.score += target['points']
        self.combo += 1
        self.combo_timer = 2.0  # Reset combo timer

        # Track max combo
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        # Check achievements
        if not self.achievements['first_target']:
            self.check_achievement('first_target', "First Blood!")

        if self.combo >= 10 and not self.achievements['combo_10']:
            self.check_achievement('combo_10', "Combo Master x10!")

        if self.combo >= 50 and not self.achievements['combo_50']:
            self.check_achievement('combo_50', "UNSTOPPABLE x50!")

        if self.score >= 1000 and not self.achievements['score_1000']:
            self.check_achievement('score_1000', "Score: 1000 Points!")

        if self.score >= 5000 and not self.achievements['score_5000']:
            self.check_achievement('score_5000', "LEGENDARY: 5000 Points!")

        # Remove target
        self.targets.remove(target)

    def update(self, dt):
        """Update architect mode"""
        if not self.active:
            return

        self.timer += dt

        # Update position
        self.arch_pos += self.arch_vel * dt

        # Keep in bounds with wrapping
        if self.arch_pos.x < 0:
            self.arch_pos.x = 1280
        elif self.arch_pos.x > 1280:
            self.arch_pos.x = 0
        if self.arch_pos.y < 0:
            self.arch_pos.y = 720
        elif self.arch_pos.y > 720:
            self.arch_pos.y = 0

        # Rotate ARCHON
        self.arch_rotation += dt * 30

        # Update orbs
        new_orbs = []
        for orb in self.orbs:
            orb['pos'] += orb['vel'] * dt
            orb['lifetime'] -= dt
            if orb['lifetime'] > 0 and 0 <= orb['pos'].x <= 1280 and 0 <= orb['pos'].y <= 720:
                new_orbs.append(orb)
        self.orbs = new_orbs

        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        # Update storm particles
        for particle in self.storm_particles:
            particle['pos'] += particle['vel'] * dt

            # Wrap around screen
            if particle['pos'].x < 0:
                particle['pos'].x = 1280
            elif particle['pos'].x > 1280:
                particle['pos'].x = 0
            if particle['pos'].y < 0:
                particle['pos'].y = 720
            elif particle['pos'].y > 720:
                particle['pos'].y = 0

        # Spawn energy spheres
        self.spawn_sphere_timer += dt
        if self.spawn_sphere_timer >= 5.0:
            self.spawn_energy_sphere()
            self.spawn_sphere_timer = 0.0

        # Update energy spheres
        new_spheres = []
        for sphere in self.energy_spheres:
            sphere['pulse'] += dt * 5
            sphere['lifetime'] -= dt

            # Check collection
            dist = (sphere['pos'] - self.arch_pos).length()
            if dist < 80:
                # Collected!
                self.power_level = min(3.0, self.power_level + 0.2)
                print(f"POWER INCREASED! Level: {self.power_level:.1f}x")
            elif sphere['lifetime'] > 0:
                new_spheres.append(sphere)

        self.energy_spheres = new_spheres

        # Check if power level maxed
        if self.power_level >= 3.0 and not self.achievements['power_maxed']:
            self.check_achievement('power_maxed', "MAXIMUM POWER!")

        # Spawn targets
        self.spawn_target_timer += dt
        spawn_rate = max(1.0, 3.0 - (self.combo / 50.0))  # Faster spawns at higher combos
        if self.spawn_target_timer >= spawn_rate:
            self.spawn_target()
            self.spawn_target_timer = 0.0

        # Update targets
        new_targets = []
        for target in self.targets:
            target['pos'] += target['vel'] * dt
            target['pulse'] += dt * 3
            target['rotation'] += dt * 50

            # Bounce off edges
            if target['pos'].x < 50 or target['pos'].x > 1230:
                target['vel'].x *= -1
            if target['pos'].y < 50 or target['pos'].y > 670:
                target['vel'].y *= -1

            # Clamp position
            target['pos'].x = max(50, min(1230, target['pos'].x))
            target['pos'].y = max(50, min(670, target['pos'].y))

            # Check collision with orbs
            destroyed = False
            for orb in self.orbs:
                dist = (orb['pos'] - target['pos']).length()
                if dist < target['size']:
                    # Hit!
                    target['health'] -= 1
                    orb['lifetime'] = 0  # Destroy orb
                    if target['health'] <= 0:
                        self.destroy_target(target)
                        destroyed = True
                        break

            if not destroyed:
                new_targets.append(target)

        self.targets = new_targets

        # Update combo timer
        if self.combo > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Combo broke
                print(f"COMBO ENDED: {self.combo}x")
                self.combo = 0

        # Update achievement popup timer
        if self.achievement_popup_timer > 0:
            self.achievement_popup_timer -= dt

        # Random lightning
        if random.random() < 0.02:
            self.spawn_lightning()

        # Update lightning bolts
        new_bolts = []
        for bolt in self.lightning_bolts:
            bolt['lifetime'] -= dt
            if bolt['lifetime'] > 0:
                new_bolts.append(bolt)
        self.lightning_bolts = new_bolts

    def spawn_lightning(self):
        """Create a lightning bolt"""
        # Random vertical or horizontal bolt
        if random.random() < 0.5:
            # Vertical
            bolt = {
                'points': [
                    (random.randint(0, 1280), 0),
                    (random.randint(0, 1280), 720)
                ],
                'lifetime': 0.2,
                'color': (200, 200, 255)
            }
        else:
            # Horizontal
            bolt = {
                'points': [
                    (0, random.randint(0, 720)),
                    (1280, random.randint(0, 720))
                ],
                'lifetime': 0.2,
                'color': (255, 200, 255)
            }
        self.lightning_bolts.append(bolt)

    def draw(self, screen):
        """Draw architect mode"""
        if not self.active:
            return

        # Draw stormy background
        screen.fill((20, 20, 40))  # Dark purple/blue

        # Draw storm particles
        for particle in self.storm_particles:
            pygame.draw.circle(screen, particle['color'],
                             (int(particle['pos'].x), int(particle['pos'].y)),
                             particle['size'])

        # Draw lightning bolts
        for bolt in self.lightning_bolts:
            alpha = int((bolt['lifetime'] / 0.2) * 255)
            for i in range(3):
                width = 3 - i
                pygame.draw.line(screen, bolt['color'],
                               bolt['points'][0], bolt['points'][1], width)

        # Draw energy spheres
        for sphere in self.energy_spheres:
            pulse_size = abs(math.sin(sphere['pulse'])) * 10 + 20
            # Glow layers
            for i in range(3):
                size = int(pulse_size + i * 5)
                alpha = 100 - i * 30
                color = (0, 255, 255)
                pygame.draw.circle(screen, color,
                                 (int(sphere['pos'].x), int(sphere['pos'].y)), size, 2)
            # Core
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(sphere['pos'].x), int(sphere['pos'].y)), 10)

        # Draw targets
        for target in self.targets:
            pulse_offset = abs(math.sin(target['pulse'])) * 5
            size = int(target['size'] + pulse_offset)

            # Draw health bar
            if target['health'] < target['max_health']:
                bar_width = target['size'] * 2
                bar_height = 5
                bar_x = target['pos'].x - bar_width / 2
                bar_y = target['pos'].y - target['size'] - 10

                # Background
                pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

                # Health
                health_width = int((target['health'] / target['max_health']) * bar_width)
                pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

            # Draw target with rotation effect (square rotated)
            # Create points for a rotating square
            points = []
            for i in range(4):
                angle = math.radians(target['rotation'] + i * 90)
                px = target['pos'].x + math.cos(angle) * size
                py = target['pos'].y + math.sin(angle) * size
                points.append((px, py))

            # Draw glow
            for i in range(3):
                glow_points = []
                glow_size = size + (3 - i) * 5
                for j in range(4):
                    angle = math.radians(target['rotation'] + j * 90)
                    px = target['pos'].x + math.cos(angle) * glow_size
                    py = target['pos'].y + math.sin(angle) * glow_size
                    glow_points.append((px, py))
                pygame.draw.polygon(screen, target['color'], glow_points, 2)

            # Draw main shape
            pygame.draw.polygon(screen, target['color'], points, 0)

            # Draw inner cross
            cross_size = size * 0.5
            pygame.draw.line(screen, (255, 255, 255),
                           (target['pos'].x - cross_size, target['pos'].y),
                           (target['pos'].x + cross_size, target['pos'].y), 2)
            pygame.draw.line(screen, (255, 255, 255),
                           (target['pos'].x, target['pos'].y - cross_size),
                           (target['pos'].x, target['pos'].y + cross_size), 2)

        # Draw orbs
        for orb in self.orbs:
            # Outer glow
            for i in range(3):
                size = orb['size'] + (3 - i) * 3
                alpha = 100 - i * 30
                pygame.draw.circle(screen, (255, 0, 255),
                                 (int(orb['pos'].x), int(orb['pos'].y)), size)
            # Inner core
            pygame.draw.circle(screen, (255, 255, 255),
                             (int(orb['pos'].x), int(orb['pos'].y)), orb['size'] // 2)

        # Draw ARCHON (player)
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.archon_image, self.arch_rotation)
        rotated_rect = rotated_image.get_rect(center=(int(self.arch_pos.x), int(self.arch_pos.y)))

        # Pulsing glow effect
        pulse = abs(math.sin(self.timer * 2)) * 20 + 235
        glow_size = int(60 * self.power_level)
        for i in range(5):
            alpha = int(pulse - i * 40)
            radius = glow_size + i * 10
            pygame.draw.circle(screen, (255, 0, 255),
                             (int(self.arch_pos.x), int(self.arch_pos.y)), radius, 2)

        screen.blit(rotated_image, rotated_rect)

        # Draw UI
        font = pygame.font.Font(None, 36)
        font_large = pygame.font.Font(None, 48)

        # Score (top center)
        score_text = font_large.render(f"SCORE: {self.score}", True, (255, 255, 100))
        score_rect = score_text.get_rect(center=(640, 30))
        screen.blit(score_text, score_rect)

        # Combo (below score, with color based on combo level)
        if self.combo > 0:
            combo_color = (255, 255, 255)
            if self.combo >= 50:
                combo_color = (255, 50, 255)  # Purple for insane combos
            elif self.combo >= 25:
                combo_color = (255, 100, 100)  # Red for high combos
            elif self.combo >= 10:
                combo_color = (255, 200, 100)  # Orange for medium combos

            combo_text = font_large.render(f"COMBO: {self.combo}x", True, combo_color)
            combo_rect = combo_text.get_rect(center=(640, 70))
            screen.blit(combo_text, combo_rect)

            # Combo timer bar
            bar_width = 200
            bar_height = 8
            bar_x = 640 - bar_width / 2
            bar_y = 95
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            combo_bar_width = int((self.combo_timer / 2.0) * bar_width)
            pygame.draw.rect(screen, combo_color, (bar_x, bar_y, combo_bar_width, bar_height))

        # Power level (top left)
        power_text = font.render(f"POWER: {self.power_level:.1f}x", True, (100, 255, 255))
        screen.blit(power_text, (20, 20))

        # Stats (top right)
        stats_x = 1100
        max_combo_text = font.render(f"MAX COMBO: {self.max_combo}x", True, (200, 200, 200))
        screen.blit(max_combo_text, (stats_x, 20))

        targets_text = font.render(f"TARGETS: {len(self.targets)}", True, (200, 200, 200))
        screen.blit(targets_text, (stats_x, 55))

        # Instructions (bottom left)
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "WASD: Float",
            "SPACE: Shoot",
            "Shoot Targets!",
            "ESC: Exit"
        ]
        y = 620
        for line in instructions:
            text = font_small.render(line, True, (180, 180, 200))
            screen.blit(text, (20, y))
            y += 25

        # Achievement popup
        if self.achievement_popup and self.achievement_popup_timer > 0:
            popup_font = pygame.font.Font(None, 56)
            alpha = min(255, int(self.achievement_popup_timer * 100))
            popup_pulse = abs(math.sin(self.timer * 8)) * 30 + 225

            # Background
            popup_bg = pygame.Surface((800, 100), pygame.SRCALPHA)
            popup_bg.fill((0, 0, 0, 150))
            screen.blit(popup_bg, (240, 250))

            # Text
            popup_text = popup_font.render(f"★ {self.achievement_popup} ★", True,
                                          (int(popup_pulse), int(popup_pulse * 0.8), 100))
            popup_rect = popup_text.get_rect(center=(640, 300))
            screen.blit(popup_text, popup_rect)

        # Title (bottom center)
        title_font = pygame.font.Font(None, 48)
        title_pulse = abs(math.sin(self.timer * 3)) * 30 + 225
        title_text = title_font.render("SYSTEM ARCHITECT MODE", True,
                                      (int(title_pulse), int(title_pulse * 0.5), int(title_pulse)))
        title_rect = title_text.get_rect(center=(640, 690))
        screen.blit(title_text, title_rect)
