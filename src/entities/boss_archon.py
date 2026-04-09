# src/entities/boss_archon.py
import pygame
import math
import random


class ARCHON(pygame.sprite.Sprite):
    """The final boss - the corrupted system core"""
    
    def __init__(self, pos):
        super().__init__()
        
        # Visual setup
        self.create_core_visual()
        self.rect = self.image.get_rect(center=pos)
        self.base_pos = pygame.Vector2(pos)
        
        # Boss stats
        self.max_health = 100
        self.health = self.max_health
        self.phase = 1  # 1, 2, or 3
        self.invulnerable = False
        self.invuln_timer = 0
        
        # Movement
        self.float_time = 0
        self.move_pattern = "floating"  # floating, aggressive, defensive, spiral

        # Spiral movement (Phase 2 arena)
        self.spiral_angle = 0.0
        self.spiral_radius = 150
        self.spiral_speed = 1.0  # Radians per second
        self.spiral_center = pygame.Vector2(640, 360)  # Will be set by arena
        
        # Attack system
        self.attack_cooldown = 0
        self.attack_pattern = 0
        self.projectiles = pygame.sprite.Group()
        
        # Visual effects
        self.rings = []
        self.corruption_particles = []
        self.pulse_scale = 1.0
        self.damage_flash = 0
        
        # Player reference (set later)
        self.player = None
        
    def create_core_visual(self):
        """Create the ARCHON core visual"""
        size = 120
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
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
            pygame.draw.polygon(self.image, color, scaled_points, 2)
        
        # Central eye
        pygame.draw.circle(self.image, (255, 255, 255), (center, center), 15)
        pygame.draw.circle(self.image, (255, 0, 255), (center, center), 10)
        pygame.draw.circle(self.image, (0, 0, 0), (center, center), 5)
        
    def set_player(self, player):
        """Set player reference for targeting"""
        self.player = player
        
    def take_damage(self, amount):
        """Handle taking damage"""
        if not self.invulnerable:
            self.health -= amount
            self.damage_flash = 0.3
            
            # Check phase transitions
            if self.health <= 66 and self.phase == 1:
                self.phase = 2
                self.move_pattern = "aggressive"
                print("ARCHON: ENTERING PHASE 2 - AGGRESSIVE PROTOCOLS")
            elif self.health <= 33 and self.phase == 2:
                self.phase = 3
                self.move_pattern = "defensive"
                print("ARCHON: CRITICAL - FINAL PHASE INITIATED")
            elif self.health <= 0:
                self.die()
                
    def die(self):
        """Handle boss death"""
        print("ARCHON CORE DESTROYED - SYSTEM STABILIZING...")
        # Create death explosion effect
        for i in range(20):
            angle = random.random() * math.pi * 2
            speed = random.uniform(100, 300)
            particle = {
                'pos': pygame.Vector2(self.rect.center),
                'vel': pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                'life': 1.0,
                'color': random.choice([(255, 0, 255), (0, 255, 255), (255, 255, 255)])
            }
            self.corruption_particles.append(particle)
        self.kill()
        
    def update(self, dt):
        """Update boss behavior"""
        if not self.player:
            return
            
        # Movement patterns
        self.float_time += dt
        
        if self.move_pattern == "floating":
            # Gentle floating movement
            self.rect.centerx = self.base_pos.x + math.sin(self.float_time) * 50
            self.rect.centery = self.base_pos.y + math.cos(self.float_time * 0.7) * 30
            
        elif self.move_pattern == "aggressive":
            # Move towards player more actively
            dx = self.player.rect.centerx - self.rect.centerx
            if abs(dx) > 200:
                self.rect.centerx += (1 if dx > 0 else -1) * 100 * dt
            self.rect.centery = self.base_pos.y + math.cos(self.float_time * 2) * 40
            
        elif self.move_pattern == "defensive":
            # Erratic movement
            if int(self.float_time * 10) % 20 == 0:
                self.rect.centerx += random.randint(-50, 50)
            self.rect.centery = self.base_pos.y + math.sin(self.float_time * 3) * 50

        elif self.move_pattern == "spiral":
            # Spiral movement for Phase 2 arena
            self.spiral_angle += self.spiral_speed * dt

            # Calculate spiral position
            self.rect.centerx = int(self.spiral_center.x + math.cos(self.spiral_angle) * self.spiral_radius)
            self.rect.centery = int(self.spiral_center.y + math.sin(self.spiral_angle) * self.spiral_radius)

            # Gradually expand spiral (optional)
            self.spiral_radius = min(self.spiral_radius + dt * 5, 200)
            
        # Attack patterns based on phase
        self.attack_cooldown -= dt
        if self.attack_cooldown <= 0:
            self.execute_attack()
            
        # Update visual effects
        self.update_effects(dt)
        
        # Handle invulnerability
        if self.invulnerable:
            self.invuln_timer -= dt
            if self.invuln_timer <= 0:
                self.invulnerable = False
                
        # Damage flash
        if self.damage_flash > 0:
            self.damage_flash -= dt
            
    def execute_attack(self):
        """Execute attack based on phase"""
        if not self.player:
            return
            
        if self.phase == 1:
            # Phase 1: Simple projectiles
            self.fire_projectile(0)
            self.attack_cooldown = 2.0
            
        elif self.phase == 2:
            # Phase 2: Spread shot
            for angle in [-30, 0, 30]:
                self.fire_projectile(angle)
            self.attack_cooldown = 1.5
            
        elif self.phase == 3:
            # Phase 3: Chaos mode
            for i in range(8):
                angle = i * 45
                self.fire_projectile(angle)
            self.attack_cooldown = 2.5
            
    def fire_projectile(self, angle_offset):
        """Fire a projectile at the player"""
        if not self.player:
            return
            
        # Calculate direction to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        angle = math.atan2(dy, dx) + math.radians(angle_offset)
        
        # Create projectile
        projectile = ARCHONProjectile(self.rect.center, angle)
        self.projectiles.add(projectile)
        
    def update_effects(self, dt):
        """Update visual effects"""
        # Pulse effect
        self.pulse_scale = 1.0 + math.sin(self.float_time * 5) * 0.1
        
        # Update corruption particles
        new_particles = []
        for particle in self.corruption_particles:
            particle['life'] -= dt
            if particle['life'] > 0:
                particle['pos'] += particle['vel'] * dt
                particle['vel'] *= 0.95  # Drag
                new_particles.append(particle)
        self.corruption_particles = new_particles
        
        # Generate new particles based on phase
        if random.random() < 0.1 * self.phase:
            angle = random.random() * math.pi * 2
            speed = random.uniform(50, 150)
            particle = {
                'pos': pygame.Vector2(self.rect.center),
                'vel': pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                'life': 0.5,
                'color': (255, 0, 255) if self.phase < 3 else (255, random.randint(0, 255), 255)
            }
            self.corruption_particles.append(particle)
            
    def draw(self, screen, camera_x):
        """Draw the boss with effects"""
        # Draw corruption particles
        for particle in self.corruption_particles:
            alpha = int(particle['life'] * 255)
            color = (*particle['color'], alpha)
            size = int(particle['life'] * 5)
            pygame.draw.circle(screen, color[:3], 
                             (int(particle['pos'].x - camera_x), int(particle['pos'].y)), 
                             size)
        
        # Draw energy rings
        if self.phase >= 2:
            for i in range(3):
                radius = 60 + i * 20 + math.sin(self.float_time * 3 + i) * 10
                color = (255, 100, 255, 50)
                pygame.draw.circle(screen, color[:3], 
                                 (self.rect.centerx - camera_x, self.rect.centery), 
                                 int(radius), 2)
        
        # Draw boss with damage flash
        if self.damage_flash > 0:
            flash_surface = self.image.copy()
            flash_surface.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(flash_surface, (self.rect.x - camera_x, self.rect.y))
        else:
            screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = 100
            bar_height = 8
            bar_x = self.rect.centerx - bar_width // 2 - camera_x
            bar_y = self.rect.top - 20
            
            # Background
            pygame.draw.rect(screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Health
            health_width = int((self.health / self.max_health) * bar_width)
            health_color = (255, 0, 0) if self.phase == 1 else (255, 100, 0) if self.phase == 2 else (255, 0, 255)
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
            
            # Border
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x)


class ARCHONProjectile(pygame.sprite.Sprite):
    """Projectile fired by ARCHON"""
    
    def __init__(self, pos, angle):
        super().__init__()
        
        # Visual
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 255), (8, 8), 8)
        pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 4)
        
        self.rect = self.image.get_rect(center=pos)
        
        # Movement
        self.speed = 300
        self.velocity = pygame.Vector2(
            math.cos(angle) * self.speed,
            math.sin(angle) * self.speed
        )
        self.lifetime = 3.0
        
    def update(self, dt):
        """Update projectile position"""
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            
    def draw(self, screen, camera_x):
        """Draw the projectile"""
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))
