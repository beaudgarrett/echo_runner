# src/entities/player.py
import random
import pygame
from src.core.utils import slice_spritesheet


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.animations = {
            "idle": slice_spritesheet("assets/characters/player/Biker_idle.png", 48, 48),
            "run": slice_spritesheet("assets/characters/player/Biker_run.png", 48, 48),
            "jump": slice_spritesheet("assets/characters/player/Biker_jump.png", 48, 48),
            "hurt": slice_spritesheet("assets/characters/player/Biker_hurt.png", 48, 48),
            "death": slice_spritesheet("assets/characters/player/Biker_death.png", 48, 48),
        }

        self.state = "idle"
        self.frames = self.animations[self.state]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # physics
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 250
        self.gravity = 100
        self.jump_force = -25
        self.on_ground = False
        self.facing_right = True

        # double jump mechanic
        self.max_jumps = 2  # Can jump twice (ground jump + air jump)
        self.jumps_remaining = 2
        self.jump_pressed = False  # Track if jump key is being held

        # dash
        self.dash_speed = 800
        self.dash_time = 0.15
        self.dash_timer = 0
        self.dash_charges = 5
        self.max_dash_charges = 5
        self.dashing = False
        self.trail = []
        
        # speed boost
        self.speed_boost_timer = 0
        self.base_speed = 250

        # lives
        self.lives = 3
        self.max_lives = 3
        self.invincible = False
        self.invincibility_timer = 0.0
        self.invincibility_duration = 1.0

        # audio
        self.audio = None  # Will be set by game
        self.was_on_ground = False  # Track landing state for sound

        # death state
        self.is_dead = False
        self.death_timer = 0.0
        self.respawn_delay = 1.5

        # spawn protection - prevents death on level load
        self.spawn_protection = False
        self.spawn_protection_timer = 0.0
        self.spawn_protection_duration = 0.3  # 300ms grace period

        # external
        self.platforms = []
        self.world_width = 4000
        self.screen_width = 1280
        self.screen_height = 720

        # Visual feedback callbacks (set by game.py)
        self.on_damage = None  # Called when taking damage
        self.on_energy_drink = None  # Called when collecting energy drink

    # ------------------------------------------------------
    def apply_gravity(self, dt):
        self.vel.y += self.gravity * dt
        if self.vel.y > 1500:
            self.vel.y = 1500

    # ------------------------------------------------------
    def animate(self, dt):
        self.animation_timer = getattr(self, "animation_timer", 0) + dt
        if self.animation_timer >= 0.1:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            frame = self.frames[self.frame_index]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            self.image = frame

    # ------------------------------------------------------
    def take_damage(self):
        if not self.invincible and not self.is_dead:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = 0.0
            print(f"Player hit! Lives left: {self.lives}")

            # Trigger visual feedback
            if self.on_damage:
                self.on_damage(self.rect.center, self.lives)

            # Check if player has died
            if self.lives <= 0:
                self.trigger_death()

    def trigger_death(self):
        """Instant death when touching the corrupted void"""
        if not self.is_dead:
            self.is_dead = True
            self.death_timer = 0.0
            self.state = "death"
            self.vel = pygame.Vector2(0, 0)
            # Reduce lives when falling into void
            self.lives -= 1
            # Play death sound
            if self.audio:
                self.audio.play_sfx("player_death")
            print(f"CONNECTION LOST. REBOOTING USER INSTANCE... Lives left: {self.lives}")

    def respawn(self, spawn_pos=(200, 560)):
        """Respawn player at specified position"""
        self.is_dead = False
        self.death_timer = 0.0
        self.pos = pygame.Vector2(spawn_pos)
        self.rect.topleft = spawn_pos
        self.vel = pygame.Vector2(0, 0)
        self.state = "idle"
        self.invincible = True
        self.invincibility_timer = 0.0
        # Reset double jump on respawn
        self.jumps_remaining = self.max_jumps
        self.jump_pressed = False
        print("User instance restored.")

    def flash_effect(self, screen, screen_rect=None):
        """Apply flash effect. If screen_rect is provided, use it for drawing glow."""
        if self.invincible:
            blink = int(self.invincibility_timer * 15) % 2
            if blink == 0 and screen_rect:
                glow = self.image.copy()
                glow.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
                glow.set_alpha(180)
                screen.blit(glow, screen_rect)
            self.image.set_alpha(130)
        else:
            self.image.set_alpha(255)

    # ------------------------------------------------------
    def update_trail(self, dt, screen):
        new_trail = []
        for t, alpha, image, pos in self.trail:
            alpha -= dt * 4
            if alpha > 0:
                new_trail.append((t + dt, alpha, image, pos))
                tint = random.choice([(255, 50, 255), (50, 255, 255), (255, 255, 255)])
                faded = image.copy()
                faded.fill((*tint, 0), special_flags=pygame.BLEND_RGBA_ADD)
                faded.set_alpha(int(alpha * 255))
                screen.blit(faded, pos)
        self.trail = new_trail

    # ------------------------------------------------------
    def dash(self):
        if self.dash_charges > 0 and not self.dashing:
            self.dashing = True
            self.dash_timer = 0
            self.dash_charges -= 1
            self.trail.append((0, 1.0, self.image.copy(), self.rect.topleft))
            # Play dash sound
            if self.audio:
                self.audio.play_sfx("dash")

    # ------------------------------------------------------
    def update(self, dt):
        # Handle death state
        if self.is_dead:
            self.death_timer += dt
            # Animation continues to play death animation
            self.frames = self.animations["death"]
            self.animate(dt)
            return  # Don't process any other input when dead

        keys = pygame.key.get_pressed()

        # dash input
        if keys[pygame.K_LSHIFT] and not self.dashing:
            self.dash()

        if self.dashing:
            self.dash_timer += dt
            direction = 1 if self.facing_right else -1
            self.pos.x += direction * self.dash_speed * dt
            # clamp in dash
            if self.pos.x < 0:
                self.pos.x = 0
            if self.pos.x + self.rect.width > self.world_width:
                self.pos.x = self.world_width - self.rect.width

            if self.dash_timer % 0.03 < dt:
                self.trail.append((0, 1.0, self.image.copy(), self.rect.topleft))

            if self.dash_timer >= self.dash_time:
                self.dashing = False

        else:
            # normal move
            self.vel.x = 0
            if keys[pygame.K_a]:
                self.vel.x = -self.speed * dt
                self.facing_right = False
            elif keys[pygame.K_d]:
                self.vel.x = self.speed * dt
                self.facing_right = True

            # Jump logic - allow double jump
            jump_keys_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

            if jump_keys_pressed and not self.jump_pressed and self.jumps_remaining > 0:
                # Perform jump
                self.vel.y = self.jump_force
                self.jumps_remaining -= 1
                self.on_ground = False

                # Play jump sound
                if self.audio:
                    self.audio.play_sfx("jump")

                # Print feedback for double jump
                if self.jumps_remaining == 0:
                    print("Double jump activated!")

            # Track if jump key is being held to prevent continuous jumping
            self.jump_pressed = jump_keys_pressed

            self.apply_gravity(dt)

            self.pos.x += self.vel.x
            self.pos.y += self.vel.y

        # clamp x
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.x + self.rect.width > self.world_width:
            self.pos.x = self.world_width - self.rect.width

        # apply to rect
        prev_bottom = self.rect.bottom
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        # platforms - "The Ground Is a Lie" mechanic
        self.on_ground = False
        for platform in getattr(self, "platforms", []):
            # Only collide with solid platforms (non-faded)
            if platform.is_solid and self.vel.y >= 0 and self.rect.colliderect(platform.rect):
                # Check if we were above the platform in the previous frame
                # More generous tolerance to prevent falling through at high speeds
                if prev_bottom <= platform.rect.top + 20:
                    # Snap player to top of platform
                    self.pos.y = platform.rect.top - self.rect.height
                    self.rect.y = int(self.pos.y)
                    self.vel.y = 0
                    # Play land sound when first landing (not already on ground)
                    if not self.was_on_ground and self.audio:
                        self.audio.play_sfx("land")
                    self.on_ground = True
                    # Reset double jump when landing
                    self.jumps_remaining = self.max_jumps
                    break

        # DEATH ZONE - touching anything except platforms = instant death
        # Only platforms are safe, everything else is the corrupted void
        # Don't check death zone during spawn protection
        if not self.spawn_protection and not self.on_ground and self.rect.bottom >= self.screen_height - 20:
            # Player touched the void - instant death
            self.trigger_death()

        # animation + invincibility
        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vel.x) > 0:
            self.state = "run"
        else:
            self.state = "idle"

        self.frames = self.animations[self.state]
        self.animate(dt)

        if self.invincible:
            self.invincibility_timer += dt
            if self.invincibility_timer >= self.invincibility_duration:
                self.invincible = False
        
        # Handle speed boost timer
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed = self.base_speed  # Reset to normal speed
                print("Speed boost ended")

        # Handle spawn protection timer
        if self.spawn_protection:
            self.spawn_protection_timer += dt
            if self.spawn_protection_timer >= self.spawn_protection_duration:
                self.spawn_protection = False
                self.spawn_protection_timer = 0.0

        # Update landing state for next frame
        self.was_on_ground = self.on_ground

    # ------------------------------------------------------
    def apply_energy_drink(self, duration, item_pos=None):
        self.dash_charges = self.max_dash_charges

        # Trigger visual feedback at item position (not player position)
        if self.on_energy_drink:
            particle_pos = item_pos if item_pos else self.rect.center
            self.on_energy_drink(particle_pos)
    
    def apply_speed_boost(self, duration):
        """Apply temporary speed boost"""
        self.speed_boost_timer = 3.0  # 3 seconds of speed
        self.speed = 400  # Increased speed
        print("Speed Boost activated!")
    
    def apply_life_restore(self):
        """Restore one life"""
        if self.lives < 3:
            self.lives += 1
            print(f"Life restored! Lives: {self.lives}")
        else:
            print("Lives already at maximum!")
