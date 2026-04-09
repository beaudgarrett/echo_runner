import pygame, random, math

class ScreenEffects:
    def __init__(self):
        self.shake_timer = 0
        self.shake_intensity = 0
        self.glitch_timer = 0
        self.glitch_intensity = 0
        self.rgb_offset = 0
        self.flash_timer = 0
        self.last_frame = None
        self.electric_arcs = []
        self.phase_2_mode = False  # Track if current glitch is Phase 2 mode

    # ------------------------------------------------------
    def trigger_shake(self, duration=0.4, intensity=12):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def trigger_glitch(self, duration=0.8, intensity=12, phase_2_mode=False):
        self.glitch_timer = duration
        self.glitch_intensity = intensity
        self.rgb_offset = intensity * 2
        self.flash_timer = 0.08
        self.phase_2_mode = phase_2_mode  # Track if this is Phase 2 glitch

        # DEBUG: Print glitch details
        print(f"GLITCH TRIGGERED: duration={duration}, intensity={intensity}, rgb_offset={self.rgb_offset}, phase_2_mode={phase_2_mode}")

    # ------------------------------------------------------
    def apply(self, dt, screen):
        offset = pygame.Vector2(0, 0)
        w, h = screen.get_size()

        if self.shake_timer > 0:
            self.shake_timer -= dt
            offset.x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset.y = random.randint(-self.shake_intensity, self.shake_intensity)

        current_frame = screen.copy()

        if self.glitch_timer > 0:
            self.glitch_timer -= dt

            # ULTIMATE FIX: COMPLETELY DISABLE glitch visual effects in normal levels
            # The BLEND_RGBA_ADD blending brightens background layers to create phantom platforms
            # Phase 2: Full corruption effects
            # Normal levels: ONLY screen shake, NO visual overlays
            if self.phase_2_mode:
                # === RGB Split ===
                surf = pygame.Surface((w, h), pygame.SRCALPHA)

                # Full RGB split with screen shifting (Phase 2 only)
                for color, shift in [((255, 0, 255), (-self.rgb_offset, 0)),
                                     ((0, 255, 255), (self.rgb_offset, 0))]:
                    layer = pygame.Surface((w, h), pygame.SRCALPHA)
                    layer.blit(screen, shift)
                    layer.fill((*color, 40), special_flags=pygame.BLEND_RGBA_ADD)
                    surf.blit(layer, (0, 0))

                # === Horizontal tear bands ===
                for _ in range(self.glitch_intensity * 2):
                    band_y = random.randint(0, h - 4)
                    band_h = random.randint(4, 30)
                    if band_y + band_h > h:
                        band_h = h - band_y
                    band = screen.subsurface((0, band_y, w, band_h)).copy()
                    shift_x = random.randint(-60, 60)
                    surf.blit(band, (shift_x, band_y))

                # === Flash ===
                if self.flash_timer > 0:
                    self.flash_timer -= dt
                    flash = pygame.Surface((w, h))
                    flash.fill((255, 255, 255))
                    flash.set_alpha(random.randint(40, 120))
                    surf.blit(flash, (0, 0))

                screen.blit(surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            # Normal levels: NO visual glitch effects (screen shake only)
            # Timer still counts down, but no visual rendering
            # Screen shake is handled separately via the offset return value

        self.last_frame = current_frame
        return offset
