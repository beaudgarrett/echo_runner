# src/systems/level_select.py
import pygame
from settings import WIDTH, HEIGHT


class LevelSelectMenu:
    """Secret level selection menu - activated by pressing K in tutorial"""

    def __init__(self):
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 28)
        self.font_code = pygame.font.Font(None, 64)

        self.active = False
        self.selected_level = None

        # Level options with descriptions
        self.levels = [
            {"num": 0, "name": "TUTORIAL", "desc": "Learn the basics"},
            {"num": 1, "name": "LEVEL 1", "desc": "First Simulation Layer"},
            {"num": 2, "name": "LEVEL 2", "desc": "Corrupt Sector"},
            {"num": 3, "name": "LEVEL 3", "desc": "ARCHON Core - Boss Fight"},
            {"num": "3P2", "name": "LEVEL 3 PHASE 2", "desc": "The Collapse - Rotating Arena"},
            {"num": "CODE", "name": "INVINCIBILITY CODE", "desc": "Enter secret code for invincibility"},
        ]

        self.hovered_index = 0
        self.pulse_timer = 0.0
        self.audio = None  # Will be set by game

        # Code entry system for invincibility
        self.code_digits = [0, 0, 0]  # Three digits
        self.code_cursor = 0  # Which digit is selected (0, 1, or 2)
        self.code_unlocked = False
        self.code_correct = "777"
        self.code_flash_timer = 0.0
        self.in_code_entry = False  # Whether we're in code entry mode

    def toggle(self):
        """Toggle the menu on/off"""
        self.active = not self.active
        self.selected_level = None
        if self.active:
            print("SECRET LEVEL SELECT ACTIVATED")
        else:
            print("Level select closed")

    def check_code(self):
        """Check if entered code matches the invincibility code"""
        entered_code = ''.join(str(d) for d in self.code_digits)
        if entered_code == self.code_correct and not self.code_unlocked:
            self.code_unlocked = True
            self.code_flash_timer = 2.0
            print("INVINCIBILITY MODE UNLOCKED!")
            if self.audio:
                self.audio.play_sfx("menu_select")

    def update(self, dt):
        """Update animations"""
        self.pulse_timer += dt

        # Update code flash timer
        if self.code_flash_timer > 0:
            self.code_flash_timer -= dt

    def handle_input(self, event):
        """Handle keyboard input for level selection"""
        if event.type == pygame.KEYDOWN:
            # Code entry mode controls
            if self.in_code_entry:
                if event.key == pygame.K_LEFT:
                    self.code_cursor = (self.code_cursor - 1) % 3
                    if self.audio:
                        self.audio.play_sfx("menu_beep")
                elif event.key == pygame.K_RIGHT:
                    self.code_cursor = (self.code_cursor + 1) % 3
                    if self.audio:
                        self.audio.play_sfx("menu_beep")
                elif event.key == pygame.K_UP:
                    self.code_digits[self.code_cursor] = (self.code_digits[self.code_cursor] + 1) % 10
                    self.check_code()
                    if self.audio:
                        self.audio.play_sfx("menu_beep")
                elif event.key == pygame.K_DOWN:
                    self.code_digits[self.code_cursor] = (self.code_digits[self.code_cursor] - 1) % 10
                    self.check_code()
                    if self.audio:
                        self.audio.play_sfx("menu_beep")
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_k or event.key == pygame.K_RETURN:
                    # Return to menu (don't close)
                    self.in_code_entry = False
                    if self.audio:
                        self.audio.play_sfx("menu_beep")
                return None

            # Menu navigation (when not in code entry)
            if event.key == pygame.K_UP:
                self.hovered_index = (self.hovered_index - 1) % len(self.levels)
                if self.audio:
                    self.audio.play_sfx("menu_beep")
            elif event.key == pygame.K_DOWN:
                self.hovered_index = (self.hovered_index + 1) % len(self.levels)
                if self.audio:
                    self.audio.play_sfx("menu_beep")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Check if CODE option is selected
                selected_num = self.levels[self.hovered_index]["num"]
                if selected_num == "CODE":
                    # Enter code entry mode (stay in menu)
                    self.in_code_entry = True
                    if self.audio:
                        self.audio.play_sfx("menu_select")
                    return None
                else:
                    # Select the hovered level and close menu
                    self.selected_level = selected_num
                    self.active = False
                    if self.audio:
                        self.audio.play_sfx("menu_select")
                    return self.selected_level
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_k:
                # Close menu
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_beep")
            # Number key shortcuts (1-4)
            elif event.key == pygame.K_0:
                self.selected_level = 0
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return self.selected_level
            elif event.key == pygame.K_1:
                self.selected_level = 1
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return self.selected_level
            elif event.key == pygame.K_2:
                self.selected_level = 2
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return self.selected_level
            elif event.key == pygame.K_3:
                self.selected_level = 3
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return self.selected_level
            elif event.key == pygame.K_4:
                self.selected_level = "3P2"
                self.active = False
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return self.selected_level
            elif event.key == pygame.K_5:
                # Enter code entry mode (stay in menu)
                self.in_code_entry = True
                if self.audio:
                    self.audio.play_sfx("menu_select")
                return None

        return None

    def draw(self, screen):
        """Draw the level selection menu"""
        # Dark translucent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        # Title with glitch effect
        pulse = abs(pygame.math.Vector2(1, 0).rotate(self.pulse_timer * 180).x)

        # Check if we're in code entry mode
        if self.in_code_entry:
            self.draw_code_entry(screen, pulse)
            return

        title_text = "SECRET LEVEL SELECT"
        title_surf = self.font_title.render(title_text, True, (255, 50, 255))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 120))

        # Glowing title
        for i in range(3):
            glow_color = (0, 255, 255) if i % 2 == 0 else (255, 50, 255)
            glow_surf = self.font_title.render(title_text, True, glow_color)
            glow_surf.set_alpha(int(80 * pulse))
            glow_rect = glow_surf.get_rect(center=(WIDTH // 2 + (i - 1) * 2, 120))
            screen.blit(glow_surf, glow_rect)

        screen.blit(title_surf, title_rect)

        # Level options
        start_y = 220
        spacing = 80

        for i, level in enumerate(self.levels):
            is_hovered = (i == self.hovered_index)
            y_pos = start_y + i * spacing

            # Selection highlight
            if is_hovered:
                # Animated highlight box
                highlight_width = 600 + int(pulse * 20)
                highlight_rect = pygame.Rect(
                    (WIDTH - highlight_width) // 2,
                    y_pos - 5,
                    highlight_width,
                    70
                )
                # Glowing border
                pygame.draw.rect(screen, (0, 255, 255), highlight_rect, 3, border_radius=8)
                pygame.draw.rect(screen, (255, 50, 255), highlight_rect.inflate(-6, -6), 2, border_radius=6)

                # Inner glow
                inner_surf = pygame.Surface((highlight_width - 10, 60), pygame.SRCALPHA)
                inner_surf.fill((0, 255, 255, 30))
                screen.blit(inner_surf, (highlight_rect.x + 5, highlight_rect.y + 5))

            # Level name
            level_color = (255, 255, 255) if is_hovered else (150, 150, 150)
            # Show green color for CODE option if unlocked
            if level['num'] == "CODE" and self.code_unlocked:
                level_color = (50, 255, 50)

            level_name = f"{level['num']}. {level['name']}"
            level_surf = self.font_option.render(level_name, True, level_color)
            level_rect = level_surf.get_rect(center=(WIDTH // 2, y_pos + 15))
            screen.blit(level_surf, level_rect)

            # Description (show UNLOCKED for code option if unlocked)
            desc_color = (0, 255, 255) if is_hovered else (100, 100, 100)
            desc_text = level['desc']
            if level['num'] == "CODE" and self.code_unlocked:
                desc_text = "UNLOCKED - Invincibility Active!"
                desc_color = (50, 255, 50)

            desc_surf = self.font_small.render(desc_text, True, desc_color)
            desc_rect = desc_surf.get_rect(center=(WIDTH // 2, y_pos + 45))
            screen.blit(desc_surf, desc_rect)

        # Instructions at bottom
        instructions = [
            "UP/DOWN - Navigate  |  ENTER/SPACE - Select",
            "Number Keys (0-5) - Quick Select  |  K/ESC - Close"
        ]

        inst_y = HEIGHT - 100
        for inst in instructions:
            inst_surf = self.font_small.render(inst, True, (150, 255, 150))
            inst_rect = inst_surf.get_rect(center=(WIDTH // 2, inst_y))
            screen.blit(inst_surf, inst_rect)
            inst_y += 30

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 0, 0, 40), (0, y), (WIDTH, y), 1)

    def draw_code_entry(self, screen, pulse):
        """Draw the code entry screen"""
        # Title
        title_text = "INVINCIBILITY CODE"
        title_surf = self.font_title.render(title_text, True, (50, 255, 50) if self.code_unlocked else (255, 50, 255))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 120))

        # Glowing title
        for i in range(3):
            glow_color = (50, 255, 50) if self.code_unlocked else ((0, 255, 255) if i % 2 == 0 else (255, 50, 255))
            glow_surf = self.font_title.render(title_text, True, glow_color)
            glow_surf.set_alpha(int(80 * pulse))
            glow_rect = glow_surf.get_rect(center=(WIDTH // 2 + (i - 1) * 2, 120))
            screen.blit(glow_surf, glow_rect)

        screen.blit(title_surf, title_rect)

        # Instructions
        if self.code_unlocked:
            inst_text = "CODE UNLOCKED! Press ENTER/ESC to return to menu"
            inst_color = (50, 255, 50) if int(self.code_flash_timer * 4) % 2 == 0 else (0, 255, 0)
        else:
            inst_text = "Enter Code: 777"
            inst_color = (150, 150, 150)

        inst_surf = self.font_small.render(inst_text, True, inst_color)
        inst_rect = inst_surf.get_rect(center=(WIDTH // 2, 220))
        screen.blit(inst_surf, inst_rect)

        # Code digits (centered)
        digit_y = HEIGHT // 2
        digit_spacing = 120
        total_width = digit_spacing * 2
        digit_start_x = (WIDTH - total_width) // 2

        for i, digit in enumerate(self.code_digits):
            digit_x = digit_start_x + i * digit_spacing

            # Highlight selected digit
            if i == self.code_cursor and not self.code_unlocked:
                highlight_rect = pygame.Rect(digit_x - 15, digit_y - 15, 80, 100)
                pygame.draw.rect(screen, (0, 255, 255, 100), highlight_rect, border_radius=10)
                pygame.draw.rect(screen, (0, 255, 255), highlight_rect, 4, border_radius=10)

            # Draw digit
            if self.code_unlocked:
                digit_color = (50, 255, 50) if self.code_flash_timer > 0 else (0, 255, 0)
            else:
                digit_color = (255, 255, 255) if i == self.code_cursor else (150, 150, 150)

            digit_surf = self.font_code.render(str(digit), True, digit_color)
            digit_rect = digit_surf.get_rect(center=(digit_x + 25, digit_y + 25))
            screen.blit(digit_surf, digit_rect)

        # Control instructions at bottom
        controls = [
            "LEFT/RIGHT - Select Digit  |  UP/DOWN - Change Digit",
            "ENTER/ESC - Return to Menu"
        ]

        ctrl_y = HEIGHT - 120
        for ctrl in controls:
            ctrl_surf = self.font_small.render(ctrl, True, (150, 255, 150))
            ctrl_rect = ctrl_surf.get_rect(center=(WIDTH // 2, ctrl_y))
            screen.blit(ctrl_surf, ctrl_rect)
            ctrl_y += 30

        # Scanline effect
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(screen, (0, 0, 0, 40), (0, y), (WIDTH, y), 1)
