# src/entities/enemy_drone.py
import pygame
from src.core.utils import slice_spritesheet


class EnemyDrone(pygame.sprite.Sprite):
    def __init__(self, pos, patrol_range=150, speed=150, detection_radius=400):
        super().__init__()

        self.animations = {
            "idle": slice_spritesheet("assets/characters/drones/Idle.png", 48, 48),
            "walk": slice_spritesheet("assets/characters/drones/Walk.png", 48, 48),
            "death": slice_spritesheet("assets/characters/drones/Death.png", 48, 48),
        }

        self.state = "patrol"
        self.frames = self.animations["walk"]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.animation_timer = 0
        self.animation_speed = 0.1

        self.origin_x = pos[0]
        self.direction = 1
        self.speed = speed
        self.patrol_range = patrol_range
        self.detection_radius = detection_radius
        self.player = None
        self.death_timer = 0

        # explosion
        self.explosion_radius = 0
        self.explosion_alpha = 0
        self.explosion_color = (0, 255, 255)

        # Visual feedback callbacks (set by game.py)
        self.on_killed = None  # Called when drone is eliminated

    def set_player(self, player):
        self.player = player

    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def patrol(self, dt):
        self.rect.x += self.direction * self.speed * dt
        if abs(self.rect.x - self.origin_x) >= self.patrol_range:
            self.direction *= -1

    def chase_player(self, dt):
        if not self.player:
            return

        px, py = self.player.rect.center
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < self.detection_radius:
            self.rect.x += (dx / dist) * self.speed * 1.2 * dt
            self.rect.y += (dy / dist) * self.speed * 1.2 * dt
        else:
            self.state = "patrol"

    def explode(self):
        self.state = "dead"
        self.frames = self.animations["death"]
        self.frame_index = 0
        self.animation_speed = 0.08
        self.death_timer = 0
        self.explosion_radius = 20
        self.explosion_alpha = 255

        # Trigger visual feedback (particles, ELIMINATED text, combo)
        if self.on_killed:
            self.on_killed(self.rect.center)

    def draw_explosion(self, screen):
        if self.state == "dead" and self.explosion_alpha > 0:
            surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*self.explosion_color, int(self.explosion_alpha)),
                self.rect.center,
                int(self.explosion_radius),
                width=4,
            )
            screen.blit(surf, (0, 0))

    def update(self, dt):
        if self.state == "dead":
            self.animate(dt)
            self.death_timer += dt
            self.explosion_radius += 500 * dt
            self.explosion_alpha -= 600 * dt
            if self.death_timer > 0.6:
                self.kill()
            return

        if self.player:
            self.chase_player(dt)
        else:
            self.patrol(dt)

        self.animate(dt)
