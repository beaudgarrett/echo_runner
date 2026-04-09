# src/systems/end_sequence.py
import pygame
import random
import math
from src.systems.cutscene import CutsceneManager, GlitchText


class EndSequenceManager:
    """Manages the complete endgame sequence including ARCHON defeat, player choice, and endings"""

    def __init__(self):
        self.active = False
        self.phase = "none"  # none, collapse, cinematic, choice, ending
        self.timer = 0.0

        # Sub-managers
        self.cutscene = CutsceneManager()

        # Collapse sequence
        self.collapse_particles = []
        self.screen_tear_offset = 0

        # Choice system
        self.choice_made = None  # 1 for DELETE, 2 for OVERWRITE
        self.choice_text_1 = None
        self.choice_text_2 = None

        # Credits
        self.credits_lines = [
            "",
            "ECHO RUNNER",
            "",
            "A game about consciousness, corruption, and choice",
            "",
            "You were the architect all along",
            "",
            "Thank you for playing",
            "",
            "",
            "Game solo developed by",
            "BEAU GARRETT",
            ""
        ]
        self.credits_scroll = 0

        # Callbacks
        self.on_delete_ending = None
        self.on_overwrite_ending = None

        # Audio reference
        self.audio = None

    def start(self, audio=None):
        """Start the end sequence"""
        self.active = True
        self.phase = "collapse"
        self.timer = 0.0
        self.collapse_particles = []
        self.audio = audio
        self.start_collapse_sequence()

    def start_collapse_sequence(self):
        """Start the system collapse sequence"""
        print("ARCHON: You... cannot delete yourself.")

        # Generate data fragment particles
        for i in range(100):
            particle = {
                'pos': pygame.Vector2(640, 360),  # Center
                'vel': pygame.Vector2(
                    random.uniform(-200, 200),
                    random.uniform(-200, 200)
                ),
                'life': random.uniform(2.0, 4.0),
                'max_life': random.uniform(2.0, 4.0),
                'size': random.randint(2, 8),
                'color': random.choice([(255, 255, 255), (0, 255, 255), (255, 0, 255)])
            }
            self.collapse_particles.append(particle)

        # Start collapse cutscene
        collapse_lines = [
            "> CORE NODE ARCHON: DESTROYED",
            "> SYSTEM ROOT: COMPROMISED",
            "> EXECUTING CLEANUP PROTOCOL...",
        ]
        self.cutscene.start(collapse_lines, line_duration=2.0, glitch_intensity=0.5,
                           on_complete=self.start_cinematic_sequence)

    def start_cinematic_sequence(self):
        """Start the cinematic revelation sequence"""
        self.phase = "cinematic"
        self.timer = 0.0

        cinematic_lines = [
            "> ERROR: SUBJECT CONTAINS ORIGINAL DESIGNER CONSCIOUSNESS.",
            "> IDENTITY: LEAD ENGINEER [REDACTED]",
            "> STATUS: SELF-UPLOADED",
            "",
            "...",
            "",
            "> YOU ARE THE SYSTEM NOW."
        ]
        self.cutscene.start(cinematic_lines, line_duration=2.5, glitch_intensity=0.4,
                           on_complete=self.start_choice_sequence)

    def start_choice_sequence(self):
        """Start the player choice sequence"""
        self.phase = "choice"
        self.timer = 0.0
        self.choice_made = None

        # Create choice text objects
        self.choice_text_1 = GlitchText(
            "[1] DELETE YOURSELF",
            (640, 280),
            font_size=56,
            color=(255, 100, 100)
        )
        self.choice_text_2 = GlitchText(
            "[2] OVERWRITE ARCHON",
            (640, 360),
            font_size=56,
            color=(100, 100, 255)
        )

        print("> WHAT WILL YOU DO?")
        print("Press 1 to DELETE YOURSELF")
        print("Press 2 to OVERWRITE ARCHON")

    def handle_choice_input(self, key):
        """Handle player choice input"""
        if self.phase != "choice":
            return False

        if key == pygame.K_1:
            self.choice_made = 1
            self.start_delete_ending()
            return True
        elif key == pygame.K_2:
            self.choice_made = 2
            self.start_overwrite_ending()
            return True

        return False

    def start_delete_ending(self):
        """Start the DELETE YOURSELF ending"""
        self.phase = "ending_delete"
        self.timer = 0.0

        delete_lines = [
            "SYSTEM SHUTDOWN INITIATED...",
            "",
            "YOU FREED THEM ALL.",
            "",
            "SYSTEM SHUTDOWN COMPLETE."
        ]
        self.cutscene.start(delete_lines, line_duration=2.5, glitch_intensity=0.2,
                           on_complete=self.show_credits)

        print("PATH CHOSEN: DELETE YOURSELF")
        print("The system is erased. All consciousnesses freed.")

    def start_overwrite_ending(self):
        """Start the OVERWRITE ARCHON ending"""
        self.phase = "ending_overwrite"
        self.timer = 0.0

        overwrite_lines = [
            "> ARCHON SYSTEM REPLACED.",
            "> NEW DESIGNATION: ECHO RUNNER.",
            "> INITIALIZING NEW WORLD INSTANCE...",
            "",
            "RYAN CARVER BETA TESTER MODE ACTIVATED"
        ]
        self.cutscene.start(overwrite_lines, line_duration=2.0, glitch_intensity=0.8,
                           on_complete=self.trigger_overwrite_ending)

        print("PATH CHOSEN: OVERWRITE ARCHON")
        print("You became the system. The cycle continues.")

    def show_credits(self):
        """Show credits after DELETE ending"""
        self.phase = "credits"
        self.credits_scroll = 720  # Start below screen

        # Initialize credits visual effects
        self.credits_particles = []
        self.credits_digital_rain = []
        self.credits_glitch_timer = 0.0
        self.credits_fade_alpha = 0

        # Spawn initial particles
        for i in range(100):
            particle = {
                'pos': pygame.Vector2(random.randint(0, 1280), random.randint(0, 720)),
                'vel': pygame.Vector2(random.uniform(-20, 20), random.uniform(-50, -20)),
                'size': random.randint(1, 3),
                'color': random.choice([
                    (100, 255, 255),  # Cyan
                    (255, 100, 255),  # Magenta
                    (255, 255, 100),  # Yellow
                    (100, 255, 100),  # Green
                ]),
                'alpha': random.randint(100, 255),
                'fade_speed': random.uniform(20, 50)
            }
            self.credits_particles.append(particle)

        # Initialize digital rain
        for i in range(30):
            rain = {
                'x': random.randint(0, 1280),
                'y': random.randint(-100, 720),
                'speed': random.uniform(100, 300),
                'length': random.randint(5, 15),
                'chars': [chr(random.randint(33, 126)) for _ in range(15)]
            }
            self.credits_digital_rain.append(rain)

    def trigger_overwrite_ending(self):
        """Trigger callback for overwrite ending"""
        if self.on_overwrite_ending:
            self.on_overwrite_ending()

    def update(self, dt):
        """Update end sequence"""
        if not self.active:
            return

        self.timer += dt

        # Update cutscene if active
        self.cutscene.update(dt)

        # Update phase-specific logic
        if self.phase == "collapse":
            self.update_collapse(dt)
        elif self.phase == "choice":
            self.update_choice(dt)
        elif self.phase == "credits":
            self.update_credits(dt)

    def update_collapse(self, dt):
        """Update collapse sequence"""
        # Update particles
        new_particles = []
        for particle in self.collapse_particles:
            particle['life'] -= dt
            if particle['life'] > 0:
                particle['pos'] += particle['vel'] * dt
                particle['vel'] *= 0.98  # Drag
                new_particles.append(particle)
        self.collapse_particles = new_particles

        # Screen tear effect
        self.screen_tear_offset += dt * 100

    def update_choice(self, dt):
        """Update choice sequence"""
        if self.choice_text_1:
            self.choice_text_1.update(dt)
        if self.choice_text_2:
            self.choice_text_2.update(dt)

    def update_credits(self, dt):
        """Update credits scroll"""
        self.credits_scroll -= dt * 50  # Scroll speed
        self.credits_glitch_timer += dt

        # Fade in effect
        if self.credits_fade_alpha < 255:
            self.credits_fade_alpha = min(255, self.credits_fade_alpha + dt * 100)

        # Update particles
        new_particles = []
        for particle in self.credits_particles:
            particle['pos'] += particle['vel'] * dt
            particle['alpha'] -= particle['fade_speed'] * dt

            # Respawn if faded or off screen
            if particle['alpha'] <= 0 or particle['pos'].y < 0:
                particle['pos'] = pygame.Vector2(random.randint(0, 1280), 720)
                particle['vel'] = pygame.Vector2(random.uniform(-20, 20), random.uniform(-50, -20))
                particle['alpha'] = random.randint(100, 255)
            new_particles.append(particle)
        self.credits_particles = new_particles

        # Update digital rain
        for rain in self.credits_digital_rain:
            rain['y'] += rain['speed'] * dt
            if rain['y'] > 720:
                rain['y'] = random.randint(-100, 0)
                rain['x'] = random.randint(0, 1280)
                # Randomize characters
                rain['chars'] = [chr(random.randint(33, 126)) for _ in range(rain['length'])]

    def draw(self, screen):
        """Draw end sequence"""
        if not self.active:
            return

        # Draw phase-specific visuals
        if self.phase == "collapse":
            self.draw_collapse(screen)
        elif self.phase == "cinematic":
            self.draw_cinematic(screen)
        elif self.phase == "choice":
            self.draw_choice(screen)
        elif self.phase == "credits":
            self.draw_credits(screen)
        elif self.phase == "ending_delete" or self.phase == "ending_overwrite":
            self.draw_ending(screen)

        # Draw cutscene overlay
        self.cutscene.draw(screen)

    def draw_collapse(self, screen):
        """Draw collapse sequence visuals"""
        # Draw particles
        for particle in self.collapse_particles:
            alpha = int((particle['life'] / particle['max_life']) * 255)
            color = (*particle['color'], alpha)
            pygame.draw.circle(screen, color[:3], (int(particle['pos'].x), int(particle['pos'].y)),
                             particle['size'])

        # Draw screen tear effect
        if random.random() < 0.3:
            tear_y = int(self.screen_tear_offset % 720)
            pygame.draw.line(screen, (255, 255, 255), (0, tear_y), (1280, tear_y), 2)

    def draw_cinematic(self, screen):
        """Draw cinematic sequence"""
        # Fade to dark background
        overlay = pygame.Surface((1280, 720))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Pulsing static effect
        if random.random() < 0.1:
            for i in range(50):
                x = random.randint(0, 1280)
                y = random.randint(0, 720)
                color = random.choice([(255, 255, 255), (255, 0, 255), (0, 255, 255)])
                pygame.draw.circle(screen, color, (x, y), 2)

    def draw_choice(self, screen):
        """Draw choice sequence"""
        # White terminal background
        overlay = pygame.Surface((1280, 720))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(240)
        screen.blit(overlay, (0, 0))

        # Add static noise
        if random.random() < 0.5:
            for i in range(100):
                x = random.randint(0, 1280)
                y = random.randint(0, 720)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, 2, 2))

        # Draw main prompt
        font = pygame.font.Font(None, 72)
        prompt_text = font.render("> WHAT WILL YOU DO?", True, (0, 0, 0))
        prompt_rect = prompt_text.get_rect(center=(640, 180))
        screen.blit(prompt_text, prompt_rect)

        # Draw choice options
        if self.choice_text_1:
            self.choice_text_1.color = (150, 0, 0)
            self.choice_text_1.draw(screen)
        if self.choice_text_2:
            self.choice_text_2.color = (0, 0, 150)
            self.choice_text_2.draw(screen)

        # Draw description text
        font_small = pygame.font.Font(None, 32)
        desc1 = font_small.render("Free the simulation — erase the system entirely", True, (80, 80, 80))
        desc1_rect = desc1.get_rect(center=(640, 320))
        screen.blit(desc1, desc1_rect)

        desc2 = font_small.render("Become the system — restart as its new god", True, (80, 80, 80))
        desc2_rect = desc2.get_rect(center=(640, 400))
        screen.blit(desc2, desc2_rect)

    def draw_ending(self, screen):
        """Draw ending sequence"""
        # Fade to black
        fade_alpha = min(255, int(self.timer * 100))
        overlay = pygame.Surface((1280, 720))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(fade_alpha)
        screen.blit(overlay, (0, 0))

    def draw_credits(self, screen):
        """Draw credits"""
        # Black background
        screen.fill((0, 0, 0))

        # Draw digital rain in background
        font_small = pygame.font.Font(None, 20)
        for rain in self.credits_digital_rain:
            for i in range(rain['length']):
                char_y = rain['y'] - (i * 20)
                if 0 <= char_y <= 720:
                    # Fade from bright green at head to dark at tail
                    fade = 1.0 - (i / rain['length'])
                    alpha = int(fade * 150)
                    color = (0, int(255 * fade), int(100 * fade))
                    char_surf = font_small.render(rain['chars'][i], True, color)
                    char_surf.set_alpha(alpha)
                    screen.blit(char_surf, (rain['x'], char_y))

        # Draw floating particles
        for particle in self.credits_particles:
            if 0 <= particle['pos'].x <= 1280 and 0 <= particle['pos'].y <= 720:
                alpha = int(max(0, min(255, particle['alpha'])))
                # Create surface for particle with alpha
                particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                particle_surf.set_colorkey((0, 0, 0))
                pygame.draw.circle(particle_surf, particle['color'],
                                 (particle['size'], particle['size']), particle['size'])
                particle_surf.set_alpha(alpha)
                screen.blit(particle_surf, (int(particle['pos'].x - particle['size']),
                                          int(particle['pos'].y - particle['size'])))

        # Draw scrolling credits text
        font = pygame.font.Font(None, 48)
        font_large = pygame.font.Font(None, 72)
        y = self.credits_scroll
        for i, line in enumerate(self.credits_lines):
            if 0 <= y <= 720:
                # Apply fade in effect
                text_alpha = min(255, self.credits_fade_alpha)

                # Special styling for "ECHO RUNNER" title
                if line == "ECHO RUNNER":
                    # Pulsing rainbow effect
                    pulse = abs(math.sin(self.timer * 1.5))
                    r = int(pulse * 155 + 100)
                    g = int(abs(math.sin(self.timer * 2)) * 155 + 100)
                    b = int(abs(math.cos(self.timer * 1.8)) * 155 + 100)

                    # Draw glow layers
                    for offset in [6, 4, 2]:
                        glow_surf = font_large.render(line, True, (r, g, b))
                        glow_surf.set_alpha(30)
                        glow_rect = glow_surf.get_rect(center=(640, y))
                        screen.blit(glow_surf, glow_rect.inflate(offset*2, offset*2))

                    # Main text
                    text_surface = font_large.render(line, True, (255, 255, 255))
                    text_surface.set_alpha(text_alpha)
                    text_rect = text_surface.get_rect(center=(640, y))
                    screen.blit(text_surface, text_rect)

                # Special styling for "BEAU GARRETT" - make it glow with cyan/purple
                elif line == "BEAU GARRETT":
                    # Pulsing glow effect
                    pulse = abs(math.sin(self.timer * 2)) * 30 + 225
                    glow_color = (int(pulse * 0.5), int(pulse * 0.8), int(pulse))

                    # Draw glow layers
                    for offset in [6, 4, 3, 2, 1]:
                        glow_surf = font_large.render(line, True, glow_color)
                        glow_surf.set_alpha(40)
                        glow_rect = glow_surf.get_rect(center=(640, y))
                        screen.blit(glow_surf, glow_rect.inflate(offset*2, offset*2))

                    # Draw main text in bright cyan
                    text_surface = font_large.render(line, True, (100, 255, 255))
                    text_surface.set_alpha(text_alpha)
                    text_rect = text_surface.get_rect(center=(640, y))
                    screen.blit(text_surface, text_rect)
                else:
                    # Regular text with fade
                    text_surface = font.render(line, True, (255, 255, 255))
                    text_surface.set_alpha(text_alpha)
                    text_rect = text_surface.get_rect(center=(640, y))
                    screen.blit(text_surface, text_rect)
            y += 60

        # Random glitch effects
        if self.credits_glitch_timer % 0.5 < 0.05:  # Brief glitch every 0.5 seconds
            for i in range(20):
                glitch_x = random.randint(0, 1280)
                glitch_y = random.randint(0, 720)
                glitch_width = random.randint(10, 100)
                glitch_height = random.randint(2, 5)
                glitch_color = random.choice([
                    (255, 0, 255),  # Magenta
                    (0, 255, 255),  # Cyan
                    (255, 255, 0),  # Yellow
                ])
                pygame.draw.rect(screen, glitch_color,
                               (glitch_x, glitch_y, glitch_width, glitch_height))

        # "Press any key to reboot" at end
        if self.credits_scroll < -len(self.credits_lines) * 60:
            # Pulsing reboot text
            reboot_alpha = int(abs(math.sin(self.timer * 3)) * 155 + 100)
            reboot_text = font.render("Press any key to reboot", True, (100, 255, 100))
            reboot_text.set_alpha(reboot_alpha)
            reboot_rect = reboot_text.get_rect(center=(640, 600))
            screen.blit(reboot_text, reboot_rect)
