# src/entities/npc_terminal.py
import pygame
import math
import random
from src.core.utils import load_image


class GlitchTerminal(pygame.sprite.Sprite):
    def __init__(self, pos, lore_text=None):
        super().__init__()

        try:
            self.image = load_image("assets/items/terminal.png")
            self.image = pygame.transform.scale(self.image, (64, 64))
        except:
            self.image = pygame.Surface((56, 64), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (20, 220, 200, 230), self.image.get_rect(), border_radius=4)
            pygame.draw.rect(self.image, (0, 255, 255, 100), self.image.get_rect(), 2, border_radius=4)

        self.rect = self.image.get_rect(center=pos)
        self.base_x = pos[0]
        self.base_y = pos[1]

        self.time = 0
        self.hover_amplitude = 2
        self.hover_speed = 2

        self.activation_radius = 120
        self.active = False
        self.deleted = False
        self.fadeout_timer = 0.0
        self.alpha = 255
        self.glow_phase = random.random() * math.pi
        self.read_time = 10.0
        self.timer = 0.0

        # Use custom lore or default
        if lore_text:
            self.full_text = lore_text
        else:
            self.full_text = [
                ">> SYSTEM LOG 03A:",
                "SIMULATION INSTABILITY DETECTED",
                "CONTACTING CORE NODE..."
            ]
        self.display_text = []
        self.typing_speed = 0.05
        self.typing_timer = 0
        self.text_progress = 0
        self.font = pygame.font.Font(None, 28)

    # -------------------------------------------------------------
    def update_display_text(self):
        all_text = "".join(self.full_text)
        visible = all_text[:self.text_progress]
        lines = []
        i = 0
        for line in self.full_text:
            lines.append(visible[i:i + len(line)])
            i += len(line)
        self.display_text = lines

    # -------------------------------------------------------------
    def update(self, dt, player, camera_x):
        if self.deleted:
            return

        self.time += dt
        # hover in world space
        self.rect.centery = self.base_y + math.sin(self.time * self.hover_speed) * self.hover_amplitude

        # fadeout
        if self.fadeout_timer > 0:
            self.fadeout_timer += dt
            self.alpha = max(0, 255 - int(self.fadeout_timer * 255 / 2))
            if self.alpha <= 0:
                self.deleted = True
            return

        # player distance (world coords)
        dist = math.hypot(player.rect.centerx - self.base_x, player.rect.centery - self.base_y)
        keys = pygame.key.get_pressed()

        if dist < self.activation_radius:
            if keys[pygame.K_e] and not self.active:
                self.active = True
                self.timer = 0.0
                self.display_text.clear()
                self.text_progress = 0
                print("GlitchTerminal activated — beginning system data upload...")

            if self.active:
                self.typing_timer += dt
                while (
                    self.typing_timer > self.typing_speed
                    and self.text_progress < sum(len(line) for line in self.full_text)
                ):
                    self.typing_timer -= self.typing_speed
                    self.text_progress += 1
                    self.update_display_text()

                self.timer += dt
                if self.timer >= self.read_time:
                    print("Terminal upload complete — shutting down.")
                    self.fadeout_timer = 0.01
        else:
            if self.active and not self.fadeout_timer:
                self.active = False

    # -------------------------------------------------------------
    def draw(self, screen, camera_x):
        if self.deleted:
            return

        # compute screen position from world
        draw_x = self.base_x - camera_x
        draw_y = self.rect.y

        # floating glow
        glow_alpha = int((math.sin(self.time * 6 + self.glow_phase) * 60) + 150)
        glow_color = (0, glow_alpha, glow_alpha)
        glow_rect = pygame.Rect(draw_x - 10, draw_y - 5, self.rect.width + 20, self.rect.height + 10)
        glow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, glow_rect, border_radius=8)
        glow_surface.set_alpha(self.alpha)
        screen.blit(glow_surface, (0, 0))

        img = self.image.copy()
        img.set_alpha(self.alpha)
        screen.blit(img, (draw_x, draw_y))

        if self.active:
            if not self.display_text and self.full_text:
                self.display_text = self.full_text.copy()

            flicker_strength = (math.sin(self.time * 30) + 1) * 0.5
            flicker_alpha = int(180 + 75 * flicker_strength)

            for i, line in enumerate(self.display_text):
                if random.random() < 0.02:
                    line = "".join(random.choice("█▓▒░") if random.random() < 0.15 else c for c in line)

                color_shift = random.choice([
                    (0, 255, 200),
                    (0, 200, 255),
                    (0, 255, 255),
                ])

                text_surface = self.font.render(line, True, color_shift)
                text_surface.set_alpha(flicker_alpha)
                rect = text_surface.get_rect(midtop=(draw_x + self.rect.width // 2, self.rect.bottom + 15 + i * 22))
                screen.blit(text_surface, rect)
        elif not self.fadeout_timer and not self.active:
            hint = self.font.render("PRESS [E] TO ACCESS", True, (0, 255, 255))
            hint.set_alpha(int((math.sin(self.time * 4) + 1) * 100))
            rect = hint.get_rect(midtop=(draw_x + self.rect.width // 2, self.rect.bottom + 20))
            screen.blit(hint, rect)
