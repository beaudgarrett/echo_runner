# src/core/chaos_mode.py
import pygame
import random
from src.entities.enemy_drone import EnemyDrone
from src.entities.item import EnergyDrink


class ChaosMode:
    """Infinite survival mode with increasing difficulty"""

    def __init__(self, player, platforms, world_width):
        self.player = player
        self.platforms = platforms
        self.world_width = world_width

        # Scoring
        self.score = 0
        self.survival_time = 0.0
        self.high_score = 0

        # Spawning
        self.drone_spawn_timer = 0.0
        self.drone_spawn_interval = 4.0  # Starts at 4 seconds
        self.min_spawn_interval = 1.0  # Fastest spawn rate

        self.item_spawn_timer = 0.0
        self.item_spawn_interval = 8.0  # Energy drinks every 8 seconds

        # Difficulty progression
        self.difficulty_timer = 0.0
        self.difficulty_interval = 15.0  # Increase difficulty every 15 seconds
        self.difficulty_level = 1

        # Active spawns
        self.drones = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

    def update(self, dt):
        """Update chaos mode logic"""
        self.survival_time += dt
        self.score = int(self.survival_time * 10)  # 10 points per second

        # Update difficulty
        self.difficulty_timer += dt
        if self.difficulty_timer >= self.difficulty_interval:
            self.difficulty_timer = 0.0
            self.difficulty_level += 1
            # Decrease spawn interval (faster spawns)
            self.drone_spawn_interval = max(self.min_spawn_interval,
                                           self.drone_spawn_interval - 0.3)
            print(f"Difficulty increased to level {self.difficulty_level}")

        # Spawn drones
        self.drone_spawn_timer += dt
        if self.drone_spawn_timer >= self.drone_spawn_interval:
            self.drone_spawn_timer = 0.0
            self.spawn_drone()

        # Spawn items
        self.item_spawn_timer += dt
        if self.item_spawn_timer >= self.item_spawn_interval:
            self.item_spawn_timer = 0.0
            self.spawn_item()

        # Update entities
        for drone in self.drones:
            drone.update(dt)

        for item in self.items:
            item.update(dt)

    def spawn_drone(self):
        """Spawn a drone at a random location"""
        # Choose a random platform
        if len(self.platforms) > 0:
            platform = random.choice(list(self.platforms))

            # Spawn drone above the platform
            x = random.randint(int(platform.rect.x), int(platform.rect.right - 48))
            y = platform.rect.y - 150

            drone = EnemyDrone((x, y))
            drone.set_player(self.player)

            # Increase drone speed with difficulty
            drone.speed = 100 + (self.difficulty_level * 15)

            self.drones.add(drone)

    def spawn_item(self):
        """Spawn an energy drink at a random location"""
        if len(self.platforms) > 0:
            platform = random.choice(list(self.platforms))

            # Spawn item on the platform
            x = random.randint(int(platform.rect.x), int(platform.rect.right - 32))
            y = platform.rect.y - 40

            item = EnergyDrink((x, y))
            self.items.add(item)

    def draw_hud(self, screen):
        """Draw chaos mode specific HUD"""
        width, height = screen.get_size()

        # Score
        score_text = self.font_large.render(f"{self.score}", True, (255, 50, 255))
        score_rect = score_text.get_rect(center=(width // 2, 40))
        screen.blit(score_text, score_rect)

        # Label
        label_text = self.font_small.render("CHAOS MODE SCORE", True, (0, 255, 255))
        label_rect = label_text.get_rect(center=(width // 2, 80))
        screen.blit(label_text, label_rect)

        # Difficulty level
        diff_text = self.font_medium.render(f"DIFFICULTY: {self.difficulty_level}", True, (255, 100, 100))
        diff_rect = diff_text.get_rect(topright=(width - 20, 100))
        screen.blit(diff_text, diff_rect)

        # Survival time
        time_text = self.font_small.render(f"TIME: {self.survival_time:.1f}s", True, (150, 255, 150))
        time_rect = time_text.get_rect(topleft=(20, 100))
        screen.blit(time_text, time_rect)

    def reset(self):
        """Reset chaos mode for a new game"""
        if self.score > self.high_score:
            self.high_score = self.score

        self.score = 0
        self.survival_time = 0.0
        self.drone_spawn_timer = 0.0
        self.drone_spawn_interval = 4.0
        self.item_spawn_timer = 0.0
        self.difficulty_timer = 0.0
        self.difficulty_level = 1

        # Clear all spawns
        self.drones.empty()
        self.items.empty()
