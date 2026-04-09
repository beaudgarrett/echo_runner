# src/core/level_manager.py
import pygame


class LevelManager:
    def __init__(self):
        self.level = 1
        self.stability = 0.0
        self.transitioning = False
        self.transition_alpha = 0
        self.phase_2_triggered = False  # Track if Phase 2 has been triggered
        self.trigger_phase_2 = False    # Signal to game.py that Phase 2 should start

    def update(self, dt):
        if not self.transitioning:
            self.stability += dt * 3
            if self.stability >= 100:
                # Check if we're in Level 3 and Phase 2 hasn't been triggered
                if self.level == 3 and not self.phase_2_triggered:
                    # Signal Phase 2 transition instead of level progression
                    self.trigger_phase_2 = True
                    self.phase_2_triggered = True
                    self.stability = 100  # Lock at 100%
                    print("STABILITY: 100% - ARCHON PHASE 2 INITIATING...")
                elif self.phase_2_triggered:
                    # Phase 2 is active - lock stability at 100% for endgame trigger
                    self.stability = 100
                    # Don't reset or advance levels - game.py will handle endgame
                else:
                    # Normal level progression
                    self.stability = 0
                    self.level += 1
                    if self.level > 3:
                        self.level = 3
                    self.transitioning = True
        else:
            self.transition_alpha += dt * 200
            if self.transition_alpha >= 255:
                self.transition_alpha = 0
                self.transitioning = False

    def draw(self, screen):
        font = pygame.font.Font(None, 32)
        text = font.render(f"STABILITY: {int(self.stability)}%", True, (150, 150, 255))
        screen.blit(text, (30, 20))
