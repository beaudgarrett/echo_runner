import pygame
import random
import math
from settings import WIDTH, HEIGHT, WORLD_WIDTH
from src.core.level_loader import LevelLoader
from src.entities.player import Player
from src.systems.background_manager import BackgroundManager
from src.core.level_manager import LevelManager
from src.systems.effects import ScreenEffects
from src.systems.hud import HUD
from src.systems.tutorial import Tutorial
from src.core.chaos_mode import ChaosMode
from src.systems.debris import DebrisSystem
from src.systems.intro_screen import IntroScreen
from src.systems.level_select import LevelSelectMenu
from src.systems.pause_menu import PauseMenu
from src.systems.digital_streaks import DigitalStreakSystem
from src.systems.level_transition import LevelTransition
from src.core.audio_manager import AudioManager
from src.systems.cutscene import CutsceneManager
from src.systems.end_sequence import EndSequenceManager
from src.core.save_system import SaveSystem
from src.systems.particles import ParticleBurst, EliminatedText, ComboCounter
from src.systems.font_fx import DashGainedText, SystemWarningText
from src.entities.tutorial_drone import TutorialDrone
from src.systems.phase2_arena import Phase2Arena
from src.systems.architect_mode import ArchitectMode


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # === Game States ===
        self.state = "intro"  # intro, tutorial, playing, game_over, victory, paused, chaos
        self.game_over_timer = 0.0
        self.victory_timer = 0.0
        self.in_tutorial = False
        self.died_this_session = False  # Track if player died this session (allows tutorial skip)

        # === Managers ===
        self.bg = BackgroundManager()
        self.level_manager = LevelManager()
        self.effects = ScreenEffects()
        self.hud = HUD()
        self.intro_screen = IntroScreen()
        self.tutorial = Tutorial()
        self.level_select = LevelSelectMenu()  # Secret level select menu
        self.pause_menu = PauseMenu()  # Pause menu
        self.level_transition = LevelTransition()  # Level transition vortex effect
        self.audio = AudioManager()  # Audio system for music and SFX
        self.level_select.audio = self.audio  # Give level select access to audio

        # === Endgame Systems ===
        self.cutscene = CutsceneManager()
        self.end_sequence = EndSequenceManager()
        self.end_sequence.audio = self.audio
        self.save_system = SaveSystem()
        self.beta_tester_mode = False
        self.beta_tester_unlocked = self.save_system.is_beta_tester_unlocked()
        self.player_frozen = False
        self.phase_2_transitioning = False
        self.phase_2_active = False
        self.invincibility_mode = False  # Activated by code in level select
        self.architect_mode = ArchitectMode()  # System Architect mode - become ARCHON
        self.chaos_mode = None  # Initialized when chaos mode starts
        self.debris = None  # Initialized when level loads
        self.digital_streaks = None  # Level 2 tron-like streaks

        # === Enhanced Visual Feedback Systems ===
        self.particles = ParticleBurst()  # Particle burst system
        self.eliminated_text = EliminatedText()  # ELIMINATED screen flash
        self.combo_counter = ComboCounter()  # Kill combo tracker
        self.dash_gained_text = DashGainedText()  # Dash reward notification
        self.system_warning = SystemWarningText()  # Corruption warnings
        self.tutorial_drone = None  # Practice drone for tutorial
        self.platform_flicker_timer = 0.0  # Platform instability after damage
        self.platform_flicker_interval = 0.5  # Flicker every 0.5s

        # === Phase 2 Arena System ===
        self.phase2_arena = Phase2Arena(WIDTH, HEIGHT)  # Special Phase 2 arena
        self.phase2_respawn_platform = None  # Temporary respawn platform
        self.phase2_respawn_timer = 0.0  # Timer for respawn platform duration

        # Start intro music
        self.audio.play_music("intro", fade_ms=2000)

        # === Player ===
        self.player = Player((200, 560))  # grounded spawn
        self.player.audio = self.audio  # Give player access to audio

        # Hook up visual feedback callbacks
        self.player.on_damage = self.on_player_damage
        self.player.on_energy_drink = self.on_player_energy_drink

        # === Sprite groups ===
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        # === Empty containers (populated by level loader) ===
        self.drones = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        # === Load Tutorial Level First ===
        loader = LevelLoader("data/levels/tutorial.json")
        level_data = loader.build(self.player)

        self.bg.set_level(1 if level_data["background"] == "level1" else 1)
        self.world_width = level_data["world_width"]

        self.platforms = level_data["platforms"]
        self.drones = level_data["drones"]
        self.items = level_data["items"]
        self.npcs = level_data["npcs"]
        self.boss = level_data.get("boss", None)

        # Add tutorial practice drone (positioned above platform 3 in open space)
        self.tutorial_drone = TutorialDrone((1000, 470))
        self.tutorial_drone.set_player(self.player)
        self.drones.add(self.tutorial_drone)

        # Hook up visual feedback callbacks
        self._setup_drone_callbacks()

        # REMOVED: Platform fade particle bursts (interfere with gameplay)
        # Platform fade visual effect is still visible, just no particles

        self.player.platforms = self.platforms
        self.player.world_width = self.world_width

        self.current_level = 0  # 0 for tutorial, 1-3 for main levels

        # Level 3 corruption effects
        self.level3_glitch_timer = 0.0
        self.level3_glitch_interval = 3.5  # Trigger glitch every 3.5 seconds

        # Emergency life restore system - fixes spawn bug
        self.level_start_timer = 0.0
        self.level_start_life_restored = False

        # Platform fading system
        self.platform_fade_timer = 0.0
        self.platform_fade_interval = 25.0  # Fade a platform every 25 seconds (reduced chaos)
        self.platform_fade_index = 0  # Which platform to fade next
        self.platforms_sorted = []  # Platforms sorted left to right
        self.platform_fading_enabled = True  # Can be disabled for special arenas

        # === Speed Run Timer System ===
        self.level_timer = 0.0  # Current level time
        self.total_game_timer = 0.0  # Total time for full game run
        self.level_start_time = 0.0  # When current level started
        self.game_run_started = False  # Track if player started a full game run (from level 1)

        # === Level Completion Delay ===
        self.level_complete_delay = 0.0  # Delay before transitioning after killing last drone
        self.level_complete_triggered = False  # Track if level completion has been triggered

        # === Easter Eggs (Session-based, resets each run) ===
        self.easter_eggs_collected = set()  # Set of level names where eggs are collected this session
        self.easter_egg_count = 0  # Count for this session (0-3)

    def jump_to_level(self, level_num):
        """Secret function: Jump to any level from level select menu"""
        # Reset player stats
        self.player.dash_charges = 5
        self.player.is_dead = False
        self.player.invincible = False
        self.player.trail = []

        if level_num == 0:
            # Go back to tutorial
            self.state = "tutorial"
            self.in_tutorial = True
            self.tutorial.timer = 0.0  # Reset tutorial timer
            self.player.lives = 3  # Reset lives for tutorial
            # Reset level_manager to tutorial state
            self.level_manager.level = 1
            self.level_manager.stability = 0.0
            self.level_manager.phase_2_triggered = False
            print("SECRET: Returning to tutorial...")
        elif level_num == "3P2":
            # Special: Jump directly to Level 3 Phase 2
            self.tutorial.active = False
            self.state = "playing"
            self.in_tutorial = False
            self.level_manager.level = 3
            self.level_manager.stability = 0.0  # Start at 0% - player must reach 100% to win
            self.level_manager.phase_2_triggered = True  # Mark Phase 2 as already triggered
            # Load level 3 first
            self.load_level(3)
            # Then immediately trigger Phase 2
            self.start_phase_2_transition()
            print("SECRET: Jumping directly to Level 3 Phase 2...")
        else:
            # Jump to specific level - load_level will set lives to 3
            self.tutorial.active = False
            self.state = "playing"
            self.in_tutorial = False
            # IMPORTANT: Sync level_manager.level with the actual level being loaded
            # This prevents Phase 2 from triggering in Level 2 when using level select
            self.level_manager.level = level_num
            self.level_manager.stability = 0.0
            self.level_manager.phase_2_triggered = False
            print(f"SECRET: Jumping to Level {level_num}...")
            # Use transition effect
            self.level_transition.start(level_num)

    def reset_level_entities(self):
        """Reset all level entities on player respawn - platforms, drones, items"""
        import os
        from src.core.level_loader import LevelLoader
        from src.core.utils import get_resource_path

        # CRITICAL: Ensure Phase 2 arena is deactivated on respawn
        if not self.phase_2_active:
            self.phase2_arena.deactivate()

        # Reset platform fading
        self.platform_fade_timer = 0.0
        self.platform_fade_index = 0

        # Reload level entities
        level_path = f"data/levels/level{self.current_level}.json"

        # Check if level file exists (use resource path for PyInstaller compatibility)
        abs_level_path = get_resource_path(level_path)
        if not os.path.exists(abs_level_path):
            # Just reset platforms if no level file
            for platform in self.platforms:
                platform.is_fading = False
                platform.is_solid = True
                platform.fade_alpha = 1.0
                platform.fade_timer = 0.0
                platform.image = platform.original_image.copy()
            return

        # Clear existing entities (except player)
        self.drones.empty()
        self.items.empty()

        # Reload level data
        loader = LevelLoader(level_path)
        level_data = loader.build(self.player)

        # Restore entities
        self.drones = level_data["drones"]
        self.items = level_data["items"]
        # Don't reload platforms/npcs/boss - just reset platform states

        # Reset all platforms to solid, non-fading state
        for platform in self.platforms:
            platform.is_fading = False
            platform.is_solid = True
            platform.fade_alpha = 1.0
            platform.fade_timer = 0.0
            platform.image = platform.original_image.copy()

        # Re-sort platforms for fading system
        self.platforms_sorted = sorted(list(self.platforms), key=lambda p: p.rect.x)

        print(f"Level {self.current_level} entities reset - drones and items respawned")

    def skip_tutorial(self):
        """Skip the tutorial and go straight to level 1"""
        if self.state == "tutorial":
            # Reset player stats for main game
            self.player.dash_charges = 5
            self.player.is_dead = False
            self.player.invincible = False
            self.player.trail = []  # Clear any tutorial trails

            self.tutorial.active = False
            self.state = "playing"
            self.in_tutorial = False
            # Mark tutorial as completed
            self.save_system.mark_tutorial_completed()
            # Start speed run timer
            self.level_timer = 0.0
            self.total_game_timer = 0.0
            self.game_run_started = True
            self.load_level(1)  # load_level will set lives to 3
            self.effects.trigger_glitch(0.8, 10)
            print("Tutorial skipped - entering simulation...")

    def start_chaos_mode(self):
        """Start infinite chaos mode"""
        import os
        from src.core.level_loader import LevelLoader

        print("Entering CHAOS MODE - Survive as long as you can!")

        # Reset player
        self.player.lives = 3
        self.player.dash_charges = 5
        self.player.is_dead = False
        self.player.rect.x = 200
        self.player.rect.y = 560
        self.player.pos = pygame.Vector2(200, 560)
        self.player.vel = pygame.Vector2(0, 0)
        self.player.trail = []  # Clear any previous trails

        # Clear existing entities
        self.drones.empty()
        self.items.empty()
        self.npcs.empty()
        self.platforms.empty()

        # Load chaos level
        loader = LevelLoader("data/levels/chaos.json")
        level_data = loader.build(self.player)

        self.bg.set_level(1)  # Use level 1 background (you can change to space later)
        self.world_width = level_data["world_width"]

        self.platforms = level_data["platforms"]
        self.player.platforms = self.platforms
        self.player.world_width = self.world_width

        # Initialize chaos mode manager
        self.chaos_mode = ChaosMode(self.player, self.platforms, self.world_width)

        # Set state
        self.state = "chaos"
        self.current_level = -1  # Special chaos mode level

        # Visual effect
        self.effects.trigger_glitch(1.2, 15)
        self.effects.trigger_shake(0.8, 10)

        # Play level 3 music for chaos mode (intense boss music)
        self.audio.play_music("level3", fade_ms=2000)

    def load_level(self, level_num):
        """Load a specific level"""
        import os
        from src.core.level_loader import LevelLoader
        from src.core.utils import get_resource_path

        level_path = f"data/levels/level{level_num}.json"

        # Check if level file exists (use resource path for PyInstaller compatibility)
        abs_level_path = get_resource_path(level_path)
        if not os.path.exists(abs_level_path):
            print(f"Level file not found: {level_path} (looked in {abs_level_path})")
            return
            
        print(f"Loading Level {level_num}")

        # Reset level timer for this level
        self.level_timer = 0.0

        # Reset level completion delay
        self.level_complete_delay = 0.0
        self.level_complete_triggered = False

        # CRITICAL: Completely reset Phase 2 state
        self.phase2_arena.deactivate()
        self.phase_2_active = False
        self.phase_2_transitioning = False

        # Re-enable normal platform fading
        self.platform_fading_enabled = True

        # Clear existing entities (except player)
        self.drones.empty()
        self.items.empty()
        self.npcs.empty()
        self.platforms.empty()

        # Load new level
        loader = LevelLoader(level_path)
        level_data = loader.build(self.player)
        
        # Update background
        self.bg.set_level(level_num)
        self.world_width = level_data["world_width"]
        
        # Set new entities
        self.platforms = level_data["platforms"]
        self.drones = level_data["drones"]
        self.items = level_data["items"]
        self.npcs = level_data["npcs"]
        self.boss = level_data.get("boss", None)

        # Hook up visual feedback callbacks to all drones
        self._setup_drone_callbacks()

        # REMOVED: Platform fade particle bursts (interfere with gameplay)
        # Platform fade visual effect is still visible, just no particles

        # Re-hook player callbacks (they may have been lost)
        self.player.on_damage = self.on_player_damage
        self.player.on_energy_drink = self.on_player_energy_drink

        # Update particle system level (for decay)
        self.particles.set_level(level_num)

        # Update player references FIRST
        self.player.platforms = self.platforms
        self.player.world_width = self.world_width

        # Reset player position for new level - spawn on first platform
        # First platform in level 1 is at y=650, player height is 48
        # Spawn at y=599 to ensure collision overlap (not just touching edge)
        self.player.pos = pygame.Vector2(200, 599)  # Slightly overlapping with platform
        self.player.rect.x = 200
        self.player.rect.y = 599
        self.player.vel = pygame.Vector2(0, 0)
        self.player.on_ground = True  # Start on ground
        self.player.jumps_remaining = self.player.max_jumps

        # CRITICAL: Reset death state AND force full lives on level start
        self.player.is_dead = False
        self.player.death_timer = 0.0
        self.player.lives = 3  # Force 3 lives at level start

        # Enable spawn protection to prevent instant death on level load
        self.player.spawn_protection = True
        self.player.spawn_protection_timer = 0.0

        # Clear dash trail from previous level
        self.player.trail = []

        self.current_level = level_num

        # Reset emergency life restore timer for new level
        self.level_start_timer = 0.0
        self.level_start_life_restored = False

        # Reset platform fading system for new level
        self.platform_fade_timer = 0.0
        self.platform_fade_index = 0
        # Sort platforms left to right by x position
        self.platforms_sorted = sorted(list(self.platforms), key=lambda p: p.rect.x)

        # Initialize debris system for this level
        if not self.debris:
            self.debris = DebrisSystem(self.world_width)
        self.debris.set_intensity(level_num)

        # Initialize digital streaks for level 2
        if level_num == 2:
            if not self.digital_streaks:
                self.digital_streaks = DigitalStreakSystem(self.world_width)
        else:
            self.digital_streaks = None  # Clear streaks on other levels

        # Play level-specific music with fade-in
        if level_num == 1:
            self.audio.play_music("level1", fade_ms=3000)
        elif level_num == 2:
            self.audio.play_music("level2", fade_ms=3000)
        elif level_num == 3:
            self.audio.play_music("level3", fade_ms=3000)

        # Trigger glitch effect on level transition
        self.effects.trigger_glitch(0.8, 10)

        # Print level intro message
        if level_num == 2:
            print("Entering Corrupt Sector - System instability increasing...")
        elif level_num == 3:
            print("ARCHON Core detected - Maximum corruption levels!")

    # ------------------------------------------------------------
    def update(self, dt):
        """Update all systems and maintain camera + world bounds."""

        # Handle pause menu
        if self.pause_menu.active:
            self.pause_menu.update(dt)
            return  # Don't update game while paused

        # Handle level transition
        if self.level_transition.active:
            self.level_transition.update(dt)
            # Load the new level when transition is complete
            if self.level_transition.is_complete():
                self.load_level(self.level_transition.target_level)
            return  # Don't update game during transition

        # Handle intro state
        if self.state == "intro":
            self.intro_screen.update(dt)
            return

        # Handle tutorial state
        if self.state == "tutorial":
            # Update level select menu if active
            if self.level_select.active:
                self.level_select.update(dt)
                return  # Don't update game while menu is open

            # Update tutorial skip permission - always allow skip
            self.tutorial.can_skip = True
            self.tutorial.update(dt)
            # Check if tutorial is complete
            if self.tutorial.is_complete():
                # Reset player stats for main game
                self.player.lives = 3
                self.player.dash_charges = 5
                self.player.is_dead = False
                self.player.invincible = False
                self.player.trail = []  # Clear tutorial trails

                self.state = "playing"
                self.in_tutorial = False
                # Mark tutorial as completed in save system
                self.save_system.mark_tutorial_completed()
                print("Tutorial complete - entering simulation...")
                # Start transition to Level 1
                self.level_transition.start(1)
            # Player can still move during tutorial
            self.player.platforms = self.platforms
            self.player.world_width = self.world_width
            self.player.update(dt)

            # Clamp player within world bounds
            if self.player.pos.x < 0:
                self.player.pos.x = 0
                self.player.rect.x = 0
            if self.player.pos.x + self.player.rect.width > self.world_width:
                self.player.pos.x = self.world_width - self.player.rect.width
                self.player.rect.x = int(self.player.pos.x)

            # Camera follow during tutorial
            target_x = self.player.rect.centerx - WIDTH // 2
            self.bg.camera_x = max(0, min(target_x, self.world_width - WIDTH))

            # Force player to stay on screen
            buffer = 100
            screen_left = self.bg.camera_x + buffer
            screen_right = self.bg.camera_x + WIDTH - buffer
            if self.player.rect.left < screen_left:
                self.player.pos.x = screen_left
                self.player.rect.x = int(screen_left)
            if self.player.rect.right > screen_right:
                self.player.pos.x = screen_right - self.player.rect.width
                self.player.rect.x = int(self.player.pos.x)

            # Tutorial-specific: Respawn without losing lives if player falls
            if self.player.is_dead and self.player.death_timer >= 0.5:
                # Restore the life that was lost
                if self.player.lives < 3:
                    self.player.lives = 3
                # Respawn at start
                self.player.respawn((200, 560))
                self.effects.trigger_glitch(0.3, 5, phase_2_mode=False)
                print("Tutorial respawn - lives restored")
                # Reset platforms just in case
                for platform in self.platforms:
                    platform.is_fading = False
                    platform.is_solid = True
                    platform.fade_alpha = 1.0

            # Update visual feedback systems (tutorial)
            self.particles.update(dt)
            self.eliminated_text.update(dt)
            self.combo_counter.update(dt, self.player.rect.center)
            self.dash_gained_text.update(dt)
            self.system_warning.update(dt)

            # Update tutorial drone
            if self.tutorial_drone:
                self.tutorial_drone.update(dt)

            # Update platforms (for warning glow)
            for platform in self.platforms:
                platform.update(dt)

            # Update drones
            for drone in self.drones:
                drone.update(dt)

            # Handle item pickups in tutorial
            for item in self.items:
                item.update(dt)
                if pygame.sprite.collide_rect(item, self.player):
                    # Handle different item types
                    if hasattr(item, 'item_type'):
                        if item.item_type == "energy":
                            self.player.apply_energy_drink(dt, item.rect.center)
                        elif item.item_type == "easter_egg":
                            # Easter egg collected! (Session-based)
                            level_name = "tutorial"  # Or you could skip tracking for tutorial
                            if level_name not in self.easter_eggs_collected:
                                self.easter_eggs_collected.add(level_name)
                                self.easter_egg_count += 1
                                print(f"EASTER EGG COLLECTED! Total this run: {self.easter_egg_count}/3")
                            self.audio.play_sfx("item_pickup")
                            self.particles.spawn_burst(item.rect.center, 'combo', count=30)
                            item.kill()
                            continue  # Skip normal item sound
                    else:
                        # Fallback for old items
                        self.player.apply_energy_drink(dt, item.rect.center)
                    self.audio.play_sfx("item_pickup")
                    item.kill()

            # Update NPCs in tutorial (for terminals)
            for terminal in self.npcs:
                terminal.update(dt, self.player, self.bg.camera_x)

            # Handle drone collisions in tutorial (allow practicing stomps)
            for drone in self.drones:
                # Only process collision if drone is not already dead
                if drone.state != "dead" and pygame.sprite.collide_rect(drone, self.player):
                    # IMPROVED STOMP DETECTION - Same as main game
                    player_centery = self.player.rect.centery
                    drone_top = drone.rect.top
                    drone_height = drone.rect.height

                    # Stomp detection: Player is falling AND player's center is above drone's bottom third
                    stomp_threshold = drone_top + (drone_height * 0.66)

                    is_stomping = (self.player.vel.y >= 0 and  # Player falling or at apex
                                  player_centery < stomp_threshold)  # Player's center is in top 2/3 of drone

                    if is_stomping:
                        # Player stomped the drone - kill it and bounce player
                        drone.explode()
                        self.audio.play_sfx("drone_explode")
                        # Position player on top of drone to prevent sinking through
                        self.player.rect.bottom = drone.rect.top
                        self.player.vel.y = -15  # Small bounce up
                        # Tutorial drone doesn't damage player
                    else:
                        # In tutorial, even side collisions don't damage player
                        # Just explode the drone and bounce player back
                        drone.explode()
                        self.audio.play_sfx("drone_explode")
                        # Push player back slightly
                        if self.player.rect.centerx < drone.rect.centerx:
                            self.player.vel.x = -200
                        else:
                            self.player.vel.x = 200

            return

        # Handle chaos mode state
        if self.state == "chaos":
            # Update chaos mode
            self.chaos_mode.update(dt)

            # Update player
            self.player.platforms = self.platforms
            self.player.world_width = self.world_width
            self.player.update(dt)

            # Check if player died in chaos mode
            if self.player.is_dead and self.player.death_timer >= self.player.respawn_delay:
                if self.player.lives <= 0:
                    # Game Over in chaos mode
                    self.state = "game_over"
                    self.game_over_timer = 0.0
                    self.effects.trigger_glitch(1.0, 15, phase_2_mode=False)
                    print(f"CHAOS MODE ENDED - Final Score: {self.chaos_mode.score}")
                    return
                else:
                    # Respawn in chaos mode
                    self.player.respawn((200, 560))
                    self.effects.trigger_glitch(0.5, 8, phase_2_mode=False)
                    # Reset platforms (chaos mode has its own drone/item management)
                    self.platform_fade_timer = 0.0
                    self.platform_fade_index = 0
                    for platform in self.platforms:
                        platform.is_fading = False
                        platform.is_solid = True
                        platform.fade_alpha = 1.0
                        platform.fade_timer = 0.0
                        platform.image = platform.original_image.copy()

            # Clamp player within world bounds
            if self.player.pos.x < 0:
                self.player.pos.x = 0
                self.player.rect.x = 0
            if self.player.pos.x + self.player.rect.width > self.world_width:
                self.player.pos.x = self.world_width - self.player.rect.width
                self.player.rect.x = int(self.player.pos.x)

            # Camera follow
            target_x = self.player.rect.centerx - WIDTH // 2
            self.bg.camera_x = max(0, min(target_x, self.world_width - WIDTH))
            self.bg.update(0)

            # Force player to stay on screen
            buffer = 100
            screen_left = self.bg.camera_x + buffer
            screen_right = self.bg.camera_x + WIDTH - buffer
            if self.player.rect.left < screen_left:
                self.player.pos.x = screen_left
                self.player.rect.x = int(screen_left)
            if self.player.rect.right > screen_right:
                self.player.pos.x = screen_right - self.player.rect.width
                self.player.rect.x = int(self.player.pos.x)

            # Handle collisions with chaos mode drones
            for drone in self.chaos_mode.drones:
                # Only process collision if drone is not already dead
                if drone.state != "dead" and pygame.sprite.collide_rect(drone, self.player):
                    # IMPROVED STOMP DETECTION - Much more forgiving
                    player_centery = self.player.rect.centery
                    drone_top = drone.rect.top
                    drone_height = drone.rect.height

                    # Stomp detection: Player is falling AND player's center is above drone's bottom third
                    stomp_threshold = drone_top + (drone_height * 0.66)

                    is_stomping = (self.player.vel.y >= 0 and  # Player falling or at apex
                                  player_centery < stomp_threshold)  # Player's center is in top 2/3 of drone

                    if is_stomping:
                        # Player stomped the drone - kill it and bounce player
                        drone.explode()
                        self.audio.play_sfx("drone_explode")
                        # Position player on top of drone to prevent sinking through
                        self.player.rect.bottom = drone.rect.top
                        self.player.vel.y = -15  # Small bounce up
                    else:
                        # Drone hit player from side or above - damage player
                        drone.explode()
                        self.audio.play_sfx("drone_explode")
                        self.player.take_damage()
                        # CRITICAL FIX: Disable tear bands to prevent phantom platform
                        self.effects.trigger_glitch(0.4, 6, phase_2_mode=False)
                        self.effects.trigger_shake(0.3, 6)

            # Handle item pickups in chaos mode
            for item in self.chaos_mode.items:
                if pygame.sprite.collide_rect(item, self.player):
                    if hasattr(item, 'item_type') and item.item_type == "energy":
                        self.player.apply_energy_drink(dt, item.rect.center)
                    self.audio.play_sfx("item_pickup")
                    item.kill()

            return

        # Handle game over state
        if self.state == "game_over":
            self.game_over_timer += dt
            return

        # Handle victory state
        if self.state == "victory":
            self.victory_timer += dt
            return

        # Handle Phase 2 transition cutscene
        if self.phase_2_transitioning:
            self.cutscene.update(dt)
            return

        # Handle endgame sequence
        if self.state == "endgame":
            self.end_sequence.update(dt)
            return

        # Handle System Architect mode
        if self.state == "architect":
            self.architect_mode.update(dt)
            return

        # Handle beta tester mode
        if self.state == "beta_tester":
            # Same as normal play but with visual corruption
            pass  # Falls through to normal game logic

        # --- INVINCIBILITY MODE ---
        # Check if code was unlocked in level select and activate invincibility
        if self.level_select.code_unlocked and not self.invincibility_mode:
            self.invincibility_mode = True
            print("=== INVINCIBILITY MODE ACTIVATED ===")

        # Apply invincibility if mode is active
        if self.invincibility_mode:
            self.player.invincible = True
            self.player.invincibility_timer = 0.0  # Reset timer so it never expires
            self.player.invincibility_duration = 999999.0  # Set duration to effectively infinite

        # --- EMERGENCY LIFE RESTORE SYSTEM ---
        # Force restore to 3 lives after 2 seconds if below 3 (fixes spawn bug)
        if not self.level_start_life_restored:
            self.level_start_timer += dt
            if self.level_start_timer >= 2.0:
                if self.player.lives < 3:
                    print(f"EMERGENCY: Restoring lives from {self.player.lives} to 3 (spawn bug fix)")
                    self.player.lives = 3
                self.level_start_life_restored = True

        # --- Player ---
        old_x = self.player.rect.centerx
        self.player.platforms = self.platforms
        self.player.world_width = self.world_width
        self.player.update(dt)
        player_dx = self.player.rect.centerx - old_x

        # PHASE 2 SPECIAL: Respawn platform system
        # If player falls off in Phase 2, spawn a temporary platform at top instead of dying
        if self.phase_2_active and self.player.rect.bottom >= HEIGHT - 20 and not self.player.spawn_protection:
            # Create respawn platform at top of screen
            from src.world.tiles import Platform
            if self.phase2_respawn_platform is None:
                # Spawn platform at top center of screen
                platform_x = self.phase2_arena.center_x - 200  # 400 pixels wide platform
                platform_y = 50  # Near top of screen
                self.phase2_respawn_platform = Platform(platform_x, platform_y, 400)
                self.phase2_respawn_timer = 3.0  # Platform lasts 3 seconds

                # Add to platforms list temporarily
                self.platforms.add(self.phase2_respawn_platform)
                self.player.platforms = self.platforms

                # Teleport player onto respawn platform
                self.player.pos = pygame.Vector2(self.phase2_arena.center_x - self.player.rect.width // 2, platform_y - 60)
                self.player.rect.x = int(self.player.pos.x)
                self.player.rect.y = int(self.player.pos.y)
                self.player.vel = pygame.Vector2(0, 0)
                self.player.on_ground = False
                self.player.is_dead = False  # Cancel death
                self.player.death_timer = 0.0

                # Visual feedback
                self.effects.trigger_glitch(0.5, 8, phase_2_mode=True)
                self.effects.trigger_shake(0.3, 6)
                self.particles.spawn_burst((self.player.rect.centerx, self.player.rect.centery), 'platform_fade', count=30)
                print("EMERGENCY RESPAWN - Platform spawned at top!")

        # Update respawn platform timer
        if self.phase2_respawn_platform is not None:
            self.phase2_respawn_timer -= dt
            if self.phase2_respawn_timer <= 0:
                # Remove respawn platform
                self.platforms.remove(self.phase2_respawn_platform)
                self.phase2_respawn_platform = None
                print("Respawn platform disappeared!")

        # Check if player died and should trigger game over
        if self.player.is_dead and self.player.death_timer >= self.player.respawn_delay:
            if self.player.lives <= 0:
                # Game Over
                self.state = "game_over"
                self.game_over_timer = 0.0
                self.effects.trigger_glitch(1.0, 15, phase_2_mode=False)
                print("SYSTEM FAILURE - GAME OVER")
                return
            else:
                # Respawn player
                self.player.respawn((200, 560))
                self.effects.trigger_glitch(0.5, 8, phase_2_mode=False)
                # Reset level entities - platforms, drones, items
                self.reset_level_entities()

        # --- Clamp player within world bounds FIRST ---
        if self.player.pos.x < 0:
            self.player.pos.x = 0
            self.player.rect.x = 0
            self.player.vel.x = 0
        if self.player.pos.x + self.player.rect.width > self.world_width:
            self.player.pos.x = self.world_width - self.player.rect.width
            self.player.rect.x = int(self.player.pos.x)
            self.player.vel.x = 0

        # --- Camera follow with buffer zone ---
        # Keep player in center area of screen, with some buffer
        buffer = 100  # Pixels from edge before camera starts moving

        # Calculate target camera position
        target_x = self.player.rect.centerx - WIDTH // 2

        # Clamp camera to world bounds
        self.bg.camera_x = max(0, min(target_x, self.world_width - WIDTH))
        self.bg.update(player_dx)

        # --- Force player to stay on screen ---
        # Calculate screen boundaries in world coordinates
        screen_left = self.bg.camera_x + buffer
        screen_right = self.bg.camera_x + WIDTH - buffer

        # Prevent player from going beyond screen edges
        if self.player.rect.left < screen_left:
            self.player.pos.x = screen_left
            self.player.rect.x = int(screen_left)
            self.player.vel.x = 0
        if self.player.rect.right > screen_right:
            self.player.pos.x = screen_right - self.player.rect.width
            self.player.rect.x = int(self.player.pos.x)
            self.player.vel.x = 0

        # --- Drones ---
        for drone in self.drones:
            drone.update(dt)
            # Only process collision if drone is not already dead
            if drone.state != "dead" and pygame.sprite.collide_rect(drone, self.player):
                # IMPROVED STOMP DETECTION - Much more forgiving
                player_bottom = self.player.rect.bottom
                player_centery = self.player.rect.centery
                drone_top = drone.rect.top
                drone_bottom = drone.rect.bottom
                drone_height = drone.rect.height

                # Stomp detection: Player is falling AND player's center is above drone's bottom third
                # This allows stomping from anywhere in the top 66% of the drone
                stomp_threshold = drone_top + (drone_height * 0.66)

                is_stomping = (self.player.vel.y >= 0 and  # Player falling or at apex
                              player_centery < stomp_threshold)  # Player's center is in top 2/3 of drone

                if is_stomping:
                    # Player stomped the drone - kill it and bounce player
                    drone.explode()
                    self.audio.play_sfx("drone_explode")
                    # Position player on top of drone to prevent sinking through
                    self.player.rect.bottom = drone.rect.top
                    self.player.vel.y = -15  # Small bounce up
                    # No damage to player
                else:
                    # Drone hit player from side or above - damage player
                    drone.explode()
                    self.audio.play_sfx("drone_explode")
                    self.player.take_damage()
                    # CRITICAL FIX: Disable tear bands to prevent phantom platform
                    self.effects.trigger_glitch(0.4, 6, phase_2_mode=False)
                    self.effects.trigger_shake(0.3, 6)

        # --- Auto-complete stability on Level 1-2 if all drones eliminated ---
        if self.current_level in [1, 2] and self.level_manager.stability < 100:
            # Count alive drones (exclude tutorial drone if it exists)
            alive_drones = [d for d in self.drones if d.state != "dead" and not hasattr(d, 'is_tutorial_drone')]
            if len(alive_drones) == 0:
                # All drones eliminated - start delay timer
                if not self.level_complete_triggered:
                    print(f"LEVEL {self.current_level}: All threats eliminated - Completing level...")
                    self.level_complete_triggered = True
                    self.level_complete_delay = 0.0

                # Count down delay (1.5 seconds)
                self.level_complete_delay += dt
                if self.level_complete_delay >= 1.5:
                    # Delay complete - set stability to 100%
                    print(f"LEVEL {self.current_level}: Stability: 100%")
                    self.level_manager.stability = 100.0
            else:
                # Drones remain - reset trigger
                self.level_complete_triggered = False
                self.level_complete_delay = 0.0

        # --- Debris System ---
        if self.debris:
            self.debris.update(dt, self.bg.camera_x, WIDTH)

        # --- Visual Feedback Systems ---
        self.particles.update(dt)
        self.eliminated_text.update(dt)
        self.combo_counter.update(dt, self.player.rect.center)
        self.dash_gained_text.update(dt)
        self.system_warning.update(dt)

        # --- Platform Flickering (Corruption Surge) ---
        if self.platform_flicker_timer > 0:
            self.platform_flicker_timer -= dt

            # Make random platforms flicker every 0.5 seconds
            # CRITICAL FIX: Only flicker if there are at least 2 platforms
            if len(self.platforms) >= 2 and int(self.platform_flicker_timer * 2) != int((self.platform_flicker_timer + dt) * 2):
                # Pick 2-3 random platforms to flicker
                num_platforms_to_flicker = random.randint(2, min(3, len(self.platforms)))
                platforms_to_flicker = random.sample(list(self.platforms), num_platforms_to_flicker)

                for platform in platforms_to_flicker:
                    # Toggle visibility (but keep collision)
                    if hasattr(platform, 'flickering'):
                        platform.flickering = not platform.flickering
                    else:
                        platform.flickering = True
        else:
            # Timer expired - reset ALL platform flickering
            for platform in self.platforms:
                if hasattr(platform, 'flickering'):
                    platform.flickering = False

        # --- Digital Streaks (Level 2) ---
        if self.digital_streaks:
            self.digital_streaks.update(dt, self.bg.camera_x, WIDTH)

        # --- Phase 2 Arena System ---
        # CRITICAL: Only update arena when in actual Phase 2
        if self.phase2_arena.active and self.phase_2_active and self.current_level == 3:
            self.phase2_arena.update(dt)
            # Update player platform reference (arena platforms may have changed)
            self.platforms = self.phase2_arena.get_platforms()
            self.player.platforms = self.platforms
        else:
            # SAFETY: If arena somehow got activated outside Phase 2, force deactivate it
            if self.phase2_arena.active and not self.phase_2_active:
                print("WARNING: Arena was active outside Phase 2 - force deactivating!")
                self.phase2_arena.deactivate()

        # --- Platform Fading System ---
        # Update all platforms
        for platform in self.platforms:
            platform.update(dt)

        # Timer to trigger platform fading (left to right) - only if enabled
        if self.platform_fading_enabled:
            self.platform_fade_timer += dt

            # Determine fade interval based on which platform we're on
            # First platform: 15 seconds, all others: 3 seconds
            current_fade_interval = 15.0 if self.platform_fade_index == 0 else 3.0

            if self.platform_fade_timer >= current_fade_interval:
                self.platform_fade_timer = 0.0
                # Fade the next platform in sequence
                if self.platform_fade_index < len(self.platforms_sorted):
                    self.platforms_sorted[self.platform_fade_index].start_fade()
                    print(f"Platform {self.platform_fade_index + 1} fading out!")
                    self.platform_fade_index += 1
                    self.effects.trigger_glitch(0.3, 5, phase_2_mode=False)

        # --- Items ---
        for item in self.items:
            item.update(dt)
            if pygame.sprite.collide_rect(item, self.player):
                # Handle different item types
                if hasattr(item, 'item_type'):
                    if item.item_type == "energy":
                        self.player.apply_energy_drink(dt, item.rect.center)
                    elif item.item_type == "speed":
                        self.player.apply_speed_boost(dt)
                    elif item.item_type == "life":
                        self.player.apply_life_restore()
                        # Spawn small red/pink particle burst for heart collection
                        self.particles.spawn_burst(item.rect.center, 'player_damage', count=15)
                    elif item.item_type == "easter_egg":
                        # Easter egg collected! (Session-based, resets each run)
                        level_name = f"level{self.current_level}"
                        if level_name not in self.easter_eggs_collected:
                            self.easter_eggs_collected.add(level_name)
                            self.easter_egg_count += 1
                            print(f"EASTER EGG COLLECTED: {level_name}!")
                            print(f"Total collected this run: {self.easter_egg_count}/3")
                        else:
                            print(f"Easter egg already collected for {level_name} this run")
                        # Golden particle burst
                        self.particles.spawn_burst(item.rect.center, 'combo', count=40)
                        self.audio.play_sfx("item_pickup")
                        item.kill()
                        continue  # Skip duplicate sound
                else:
                    # Fallback for old items
                    self.player.apply_energy_drink(dt, item.rect.center)
                self.audio.play_sfx("item_pickup")
                item.kill()

        # --- NPCs ---
        for terminal in self.npcs:
            terminal.update(dt, self.player, self.bg.camera_x)
        
        # --- Boss ---
        if self.boss:
            self.boss.update(dt)

            # Check boss projectiles hitting player
            if hasattr(self.boss, 'projectiles'):
                for proj in self.boss.projectiles:
                    proj.update(dt)
                    if pygame.sprite.collide_rect(proj, self.player):
                        self.player.take_damage()
                        self.audio.play_sfx("boss_attack")
                        # Use Phase 2 effects if in Phase 2
                        self.effects.trigger_glitch(0.5, 8, phase_2_mode=self.phase_2_active)
                        self.effects.trigger_shake(0.4, 8)
                        proj.kill()

            # Check player attacking boss (dash through)
            if self.player.dashing and pygame.sprite.collide_rect(self.boss, self.player):
                self.boss.take_damage(10)
                # Use Phase 2 effects if in Phase 2
                self.effects.trigger_glitch(0.3, 5, phase_2_mode=self.phase_2_active)
                self.player.dashing = False  # Stop dash on hit

            # Check if boss is defeated
            if hasattr(self.boss, 'health') and self.boss.health <= 0:
                # Check if Phase 2 is already active
                if self.phase_2_active:
                    # Phase 2 boss defeated - trigger endgame
                    self.start_endgame_sequence()
                elif not self.level_manager.phase_2_triggered:
                    # Phase 1 boss defeated - don't trigger endgame, let stability reach 100% to start Phase 2
                    # Remove the boss but don't trigger endgame
                    self.boss = None
                    print("PHASE 1 COMPLETE: Boss defeated - reach 100% stability to trigger Phase 2...")
            # Check if Phase 2 is complete (100% stability while in Phase 2)
            # Only check if boss still exists and endgame hasn't started
            elif self.phase_2_active and self.level_manager.stability >= 100 and self.boss and hasattr(self.boss, 'health'):
                print("PHASE 2 COMPLETE: 100% stability reached - Triggering endgame...")
                # Kill the boss if still alive
                if self.boss.health > 0:
                    self.boss.health = 0
                    # The boss death check above will trigger start_endgame_sequence() on next frame
                else:
                    # Boss already dead, trigger endgame directly
                    self.start_endgame_sequence()

        # --- Level 3 constant corruption effects ---
        if self.current_level == 3:
            self.level3_glitch_timer += dt
            if self.level3_glitch_timer >= self.level3_glitch_interval:
                # Trigger extremely faint periodic glitch - very subtle boss atmosphere
                # Use Phase 2 effects if in Phase 2
                self.effects.trigger_glitch(0.08, 2, phase_2_mode=self.phase_2_active)
                self.effects.trigger_shake(0.04, 1)   # Reduced from 0.08, 2
                self.level3_glitch_timer = 0.0

        # --- Speed Run Timer ---
        if self.game_run_started and self.state == "playing":
            self.level_timer += dt
            self.total_game_timer += dt

        # --- Level progression ---
        prev_level = self.level_manager.level
        self.level_manager.update(dt)

        # Check if Phase 2 should trigger (100% stability in Level 3)
        if hasattr(self.level_manager, 'trigger_phase_2') and self.level_manager.trigger_phase_2:
            self.start_phase_2_transition()
            self.level_manager.trigger_phase_2 = False  # Reset flag

        # Check if we need to load next level
        if self.level_manager.level != prev_level and self.level_manager.level <= 3:
            # Save best time for completed level
            if self.game_run_started and self.current_level > 0:
                level_name = f"level{self.current_level}"
                is_record = self.save_system.save_best_time(level_name, self.level_timer)
                if is_record:
                    print(f"NEW RECORD for {level_name}: {self.level_timer:.2f}s!")
                else:
                    best = self.save_system.get_best_time(level_name)
                    print(f"{level_name} completed in {self.level_timer:.2f}s (Best: {best:.2f}s)")
            # Start transition instead of directly loading
            self.level_transition.start(self.level_manager.level)

    # ------------------------------------------------------------
    def draw(self, dt):
        """Render everything in correct order."""
        self.screen.fill((0, 0, 0))  # clear frame

        # === Intro Screen ===
        if self.state == "intro":
            self.intro_screen.draw(self.screen)
            return

        # === Background ===
        self.bg.draw(self.screen)

        # === Debris (falling behind everything) ===
        if self.debris:
            self.debris.draw(self.screen, self.bg.camera_x)

        # === Digital Streaks (Level 2 tron-like effects) ===
        if self.digital_streaks:
            self.digital_streaks.draw(self.screen, self.bg.camera_x)

        # === Platforms ===
        # Draw Phase 2 arena (includes platforms and visual effects)
        # CRITICAL: Only draw arena when ALL conditions are met
        if (self.phase2_arena.active and self.phase_2_active and
            self.state == "playing" and self.current_level == 3):
            self.phase2_arena.draw(self.screen, int(self.bg.camera_x))
        else:
            # Normal platform drawing
            for platform in self.platforms:
                # Skip drawing if flickering (corruption surge effect)
                if not (hasattr(platform, 'flickering') and platform.flickering):
                    platform.draw(self.screen, int(self.bg.camera_x))

                    # SPECIAL: Phase 2 respawn platform - draw with pulsing warning effect
                    if platform == self.phase2_respawn_platform:
                        # Calculate pulse based on remaining time
                        pulse = abs(math.sin(self.phase2_respawn_timer * 5))
                        warning_alpha = int(pulse * 150 + 50)

                        # Draw red warning overlay on respawn platform
                        warning_surf = pygame.Surface((platform.rect.width, platform.rect.height), pygame.SRCALPHA)
                        warning_surf.fill((255, 50, 50, warning_alpha))
                        offset_x = platform.rect.x - int(self.bg.camera_x)
                        self.screen.blit(warning_surf, (offset_x, platform.rect.y))

                        # Draw timer text on platform
                        if hasattr(self, 'hud') and self.hud:
                            font = pygame.font.Font(None, 32)
                            time_text = f"{self.phase2_respawn_timer:.1f}s"
                            text_surf = font.render(time_text, True, (255, 255, 255))
                            text_x = offset_x + platform.rect.width // 2 - text_surf.get_width() // 2
                            text_y = platform.rect.y + 10
                            self.screen.blit(text_surf, (text_x, text_y))

        # === Chaos Mode Entities ===
        if self.state == "chaos" and self.chaos_mode:
            # Draw items with camera offset
            for item in self.chaos_mode.items:
                offset_rect = item.rect.copy()
                offset_rect.x -= int(self.bg.camera_x)
                self.screen.blit(item.image, offset_rect)

            # Draw drones with camera offset
            for drone in self.chaos_mode.drones:
                offset_rect = drone.rect.copy()
                offset_rect.x -= int(self.bg.camera_x)
                self.screen.blit(drone.image, offset_rect)
        else:
            # === Normal Entities ===
            # Draw items with camera offset
            for item in self.items:
                offset_rect = item.rect.copy()
                offset_rect.x -= int(self.bg.camera_x)
                self.screen.blit(item.image, offset_rect)

            # Draw drones with camera offset
            for drone in self.drones:
                offset_rect = drone.rect.copy()
                offset_rect.x -= int(self.bg.camera_x)
                self.screen.blit(drone.image, offset_rect)

            # === NPC Terminals ===
            # CRITICAL FIX: Hide terminals in Phase 2 (they shouldn't be visible in arena)
            if not self.phase_2_active:
                for terminal in self.npcs:
                    terminal.draw(self.screen, self.bg.camera_x)

            # === Boss ===
            if self.boss:
                self.boss.draw(self.screen, int(self.bg.camera_x))

        # === Player visual effects ===
        # Draw player trail with camera offset
        new_trail = []
        neon_palette = [
            (255, 50, 255),   # Hot pink
            (50, 255, 255),   # Cyan
            (255, 255, 50),   # Yellow
            (50, 255, 150),   # Green
            (255, 100, 255),  # Magenta
            (150, 50, 255),   # Purple
            (255, 150, 50)    # Orange
        ]
        for t, alpha, image, pos in self.player.trail:
            # Fade out over time
            alpha -= dt * 3.5  # Fade faster for cleaner trails
            if alpha > 0:
                offset_pos = (pos[0] - int(self.bg.camera_x), pos[1])
                # Pick color based on trail age for variety
                color_index = int(t * 10) % len(neon_palette)
                tint = neon_palette[color_index]
                faded = image.copy()
                faded.fill((*tint, 0), special_flags=pygame.BLEND_RGBA_ADD)
                faded.set_alpha(int(alpha * 255))
                self.screen.blit(faded, offset_pos)
                new_trail.append((t + dt, alpha, image, pos))
        self.player.trail = new_trail

        # Draw player with camera offset
        player_offset_rect = self.player.rect.copy()
        player_offset_rect.x -= int(self.bg.camera_x)

        # Apply flash effect with offset rect
        self.player.flash_effect(self.screen, player_offset_rect)

        # Draw player
        self.screen.blit(self.player.image, player_offset_rect)

        # === HUD ===
        if self.state == "chaos" and self.chaos_mode:
            # Draw chaos mode HUD
            self.chaos_mode.draw_hud(self.screen)
            # Also draw player lives and dashes
            self.hud.draw_lives(self.screen, self.player.lives, 20, 60)
            self.hud.draw_dash_charges(self.screen, self.player.dash_charges,
                                      self.player.max_dash_charges, WIDTH - 200, 20)
            # Draw invincibility indicator if active
            if self.invincibility_mode:
                self.hud.draw_invincibility(self.screen, WIDTH - 200, 100)
        else:
            # Draw normal HUD
            level_timer = self.level_timer if self.game_run_started else None
            self.hud.draw(self.screen, self.player, self.level_manager, self.invincibility_mode,
                         level_timer=level_timer, easter_egg_count=self.easter_egg_count)

        # === Tutorial Overlay ===
        if self.state == "tutorial":
            self.tutorial.draw(self.screen)

        # === Secret Level Select Menu ===
        if self.level_select.active:
            self.level_select.draw(self.screen)

        # === Level Transition Vortex ===
        if self.level_transition.active:
            self.level_transition.draw(self.screen)

        # === Pause Menu ===
        if self.pause_menu.active:
            self.pause_menu.draw(self.screen)

        # === Global post-effects ===
        self.effects.apply(dt, self.screen)

        # === Lives-Based Corruption Surge (PHASE 2 ONLY) ===
        # CRITICAL FIX: Only show visual corruption in Phase 2, not in normal levels
        if self.phase_2_active and self.state != "intro" and self.state != "tutorial":
            if self.player.lives == 2:
                # Light corruption: occasional static bands
                if random.random() < 0.1:  # 10% chance per frame
                    static_y = random.randint(0, HEIGHT - 50)
                    static_surf = pygame.Surface((WIDTH, 5), pygame.SRCALPHA)
                    static_surf.fill((255, 255, 255, 80))
                    self.screen.blit(static_surf, (0, static_y))
            elif self.player.lives == 1:
                # Heavy corruption: RGB channel split + dimming
                # Create RGB split effect
                screen_copy = self.screen.copy()

                # Red channel offset
                red_channel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                red_channel.blit(screen_copy, (-3, 0))
                red_channel.set_alpha(180)
                self.screen.blit(red_channel, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Cyan channel offset
                cyan_channel = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                cyan_surf = screen_copy.copy()
                cyan_surf.fill((0, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
                cyan_channel.blit(cyan_surf, (3, 0))
                cyan_channel.set_alpha(150)
                self.screen.blit(cyan_channel, (0, 0), special_flags=pygame.BLEND_ADD)

                # Dimming overlay
                dim_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dim_surf.fill((0, 0, 0, 40))
                self.screen.blit(dim_surf, (0, 0))

        # === Visual Feedback Systems (particles, text, combo) ===
        # FIXED: Text feedback systems disabled to prevent visual artifacts
        self.particles.draw(self.screen)  # Keep particles
        # self.eliminated_text.draw(self.screen)  # DISABLED - causes issues
        # self.combo_counter.draw(self.screen)  # Keep disabled for now
        # self.dash_gained_text.draw(self.screen)  # Keep disabled for now
        # self.system_warning.draw(self.screen)  # Keep disabled for now

        # === Tutorial Drone Instruction Text ===
        # DISABLED: Text above drone removed - tutorial text now explains jumping on drones
        # if self.tutorial_drone and self.state == "tutorial":
        #     self.tutorial_drone.draw_instruction(self.screen, int(self.bg.camera_x))

        # === Game Over Screen ===
        if self.state == "game_over":
            self.draw_game_over()

        # === Victory Screen ===
        if self.state == "victory":
            self.draw_victory()

        # === Phase 2 transition cutscene ===
        if self.phase_2_transitioning:
            self.cutscene.draw(self.screen)

        # === Endgame Sequence ===
        if self.state == "endgame":
            self.end_sequence.draw(self.screen)

        # === System Architect Mode ===
        if self.state == "architect":
            self.architect_mode.draw(self.screen)

        # === Phase 2 Active Indicator ===
        if self.phase_2_active and not self.beta_tester_mode:
            font = pygame.font.Font(None, 42)
            text = font.render("PHASE 2: THE COLLAPSE", True, (255, 50, 50))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            if random.random() < 0.9:  # Flicker effect
                self.screen.blit(text, text_rect)

        # === Beta Tester Mode Indicator ===
        if self.beta_tester_mode:
            font = pygame.font.Font(None, 36)
            text = font.render("RYAN CARVER BETA TESTER MODE", True, (255, 0, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, 50))
            if random.random() < 0.8:  # Glitch flicker
                self.screen.blit(text, text_rect)

            dash_text = font.render("DASHES: UNLIMITED", True, (0, 255, 255))
            dash_rect = dash_text.get_rect(center=(WIDTH // 2, 90))
            self.screen.blit(dash_text, dash_rect)

    # ------------------------------------------------------------

    def start_phase_2_transition(self):
        """Start Phase 2 transition sequence at 100% stability"""
        print("=== PHASE 2 TRANSITION TRIGGERED ===")

        # Freeze player
        self.player_frozen = True

        # Trigger massive glitch (Phase 2 mode enabled)
        self.effects.trigger_glitch(3.0, 15, phase_2_mode=True)
        self.effects.trigger_shake(2.0, 12)

        # Start Phase 2 cutscene
        phase_2_lines = [
            "> SYSTEM STABILITY: 100%",
            "> CORE NODE IDENTIFIED...",
            "> ENTITY: ARCHON_OMEGA",
            "> INITIALIZING COUNTERMEASURES..."
        ]

        def on_phase_2_cutscene_complete():
            self.enter_phase_2_arena()

        self.cutscene.start(phase_2_lines, line_duration=2.0, glitch_intensity=0.6,
                           on_complete=on_phase_2_cutscene_complete)

        # Change state to phase transition
        self.phase_2_transitioning = True

    def enter_phase_2_arena(self):
        """Enter Phase 2 enhanced arena with rotating platforms"""
        print("ENTERING PHASE 2 ARENA - THE COLLAPSE")

        # Reset stability to 0 - player must reach 100% again to complete Phase 2
        self.level_manager.stability = 0.0
        print("PHASE 2: Stability reset to 0% - reach 100% to defeat ARCHON!")

        # Visual transformation (Phase 2 mode enabled)
        self.effects.trigger_glitch(2.0, 10, phase_2_mode=True)

        # Activate Phase 2 Arena
        self.phase2_arena.activate()

        # Replace platforms with arena platforms
        self.platforms = self.phase2_arena.get_platforms()
        self.player.platforms = self.platforms

        # Disable normal platform fading (arena handles its own platforms)
        self.platform_fading_enabled = False

        # Teleport player to arena center (on the initial platform)
        player_spawn_x = self.phase2_arena.center_x - self.player.rect.width // 2
        player_spawn_y = self.phase2_arena.center_y - 50  # Slightly above platform
        self.player.pos = pygame.Vector2(player_spawn_x, player_spawn_y)
        self.player.rect.x = int(player_spawn_x)
        self.player.rect.y = int(player_spawn_y)
        self.player.vel = pygame.Vector2(0, 0)

        # CRITICAL FIX: Reposition items for Phase 2 arena
        # Place Monster Energy ABOVE platform to the right
        for item in self.items:
            if hasattr(item, 'item_type') and item.item_type == "energy":
                # Position to the right of center, ABOVE the platform
                item.rect.x = int(self.phase2_arena.center_x + 200)
                item.rect.y = int(self.phase2_arena.center_y - 120)  # Well above platform
            else:
                # Position other items around the arena (above platforms)
                item.rect.x = int(self.phase2_arena.center_x + random.randint(-150, 150))
                item.rect.y = int(self.phase2_arena.center_y - random.randint(100, 150))

        # If boss exists, enhance it for Phase 2
        if self.boss:
            # Enhance the boss
            self.boss.phase = 2
            if hasattr(self.boss, 'is_phase_2_mode'):
                self.boss.is_phase_2_mode = True
            self.boss.max_health = 150  # More health for Phase 2
            self.boss.health = 150

            # CRITICAL FIX: Add 5 second delay before boss starts shooting
            # This prevents instant damage when player spawns in Phase 2
            self.boss.attack_cooldown = 5.0

            # Set boss to SPIRAL movement pattern
            self.boss.move_pattern = "spiral"
            self.boss.spiral_center = self.phase2_arena.spiral_center  # Use arena center
            self.boss.spiral_radius = 280  # Larger circle for Phase 2 (was 150)

            # Visual effect - boss transforms
            import math
            for i in range(50):
                angle = random.random() * math.pi * 2
                speed = random.uniform(200, 400)
                particle = {
                    'pos': pygame.Vector2(self.boss.rect.center),
                    'vel': pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                    'life': 1.5,
                    'color': random.choice([(255, 0, 255), (0, 255, 255), (255, 255, 255)])
                }
                if hasattr(self.boss, 'corruption_particles'):
                    self.boss.corruption_particles.append(particle)

            print("ARCHON ENHANCED - Phase 2 SPIRAL MODE active")

        # Unfreeze player
        self.player_frozen = False
        self.phase_2_transitioning = False
        self.phase_2_active = True

        print("PHASE 2 ACTIVE - Rotating platform arena! Platform splits in 15 seconds!")

    # ============================================================
    # VISUAL FEEDBACK CALLBACKS
    # ============================================================

    def _setup_drone_callbacks(self):
        """Hook up visual feedback callbacks to all drones"""
        for drone in self.drones:
            # Skip tutorial drone (it has special behavior)
            if hasattr(drone, 'is_tutorial_drone') and drone.is_tutorial_drone:
                drone.on_killed = self.on_tutorial_drone_killed
            else:
                drone.on_killed = self.on_drone_killed

    def on_drone_killed(self, pos):
        """Called when a regular drone is eliminated"""
        # Spawn magenta particle burst
        self.particles.spawn_burst(pos, 'drone_kill')

        # Trigger ELIMINATED text with screen flash
        font = pygame.font.Font(None, 64)
        self.eliminated_text.trigger(font)

        # Trigger screen effects
        self.effects.trigger_shake(0.3, 5)
        # Use Phase 2 effects if in Phase 2
        self.effects.trigger_glitch(0.5, 8, phase_2_mode=self.phase_2_active)

        # Add to combo counter
        font_small = pygame.font.Font(None, 48)
        dash_awarded = self.combo_counter.add_kill(font_small)

        # Award dash for combo milestone
        if dash_awarded and self.player.dash_charges < self.player.max_dash_charges:
            self.player.dash_charges += 1
            font_tiny = pygame.font.Font(None, 32)
            self.dash_gained_text.trigger(font_tiny, (WIDTH - 150, 60))
            print(f"COMBO x{self.combo_counter.combo} - DASH GAINED!")

    def on_tutorial_drone_killed(self, pos):
        """Called when tutorial practice drone is eliminated (no combo)"""
        # Only particle burst, no ELIMINATED text or combo in tutorial
        self.particles.spawn_burst(pos, 'drone_kill')
        self.effects.trigger_shake(0.2, 3)

    def on_player_damage(self, pos, lives_remaining):
        """Called when player takes damage"""
        # Spawn red particle burst
        self.particles.spawn_burst(pos, 'player_damage', count=30)

        # Trigger corruption surge based on lives
        # CRITICAL FIX: Only use severe tear bands in Phase 2 to prevent phantom platform artifacts
        self.effects.trigger_glitch(2.0, 8 + (3 - lives_remaining) * 2, phase_2_mode=self.phase_2_active)
        self.effects.trigger_shake(0.5, 6)

        # Show system warning
        font = pygame.font.Font(None, 36)
        self.system_warning.trigger(font, "SYSTEM INTEGRITY: CRITICAL")

        # ONLY trigger platform flickering in Phase 2 (prevents normal levels from breaking)
        if self.phase_2_active:
            self.platform_flicker_timer = 5.0

    def on_player_energy_drink(self, pos):
        """Called when player collects energy drink"""
        # Spawn cyan particle burst (15-20 particles)
        self.particles.spawn_burst(pos, 'energy_drink')

    # ------------------------------------------------------------

    def start_endgame_sequence(self):
        """Start the complete endgame sequence"""
        # Freeze player
        self.player_frozen = True

        # Start end sequence
        self.end_sequence.start(audio=self.audio)

        # Set callbacks
        self.end_sequence.on_delete_ending = self.trigger_delete_ending
        self.end_sequence.on_overwrite_ending = self.trigger_overwrite_ending

        # Set state
        self.state = "endgame"

        # Remove boss
        self.boss = None

        print("=== ENDGAME SEQUENCE INITIATED ===")

    def trigger_delete_ending(self):
        """Handle DELETE YOURSELF ending"""
        print("PATH: DELETE YOURSELF - System erased")
        # Mark perfect run if applicable
        if self.player.lives == self.player.max_lives:
            self.save_system.mark_perfect_run()

    def trigger_overwrite_ending(self):
        """Handle OVERWRITE ARCHON ending - leads to System Architect Mode"""
        print("PATH: OVERWRITE ARCHON - Becoming the system")

        # Unlock Beta Tester Mode if perfect run
        if self.player.lives == self.player.max_lives:
            self.save_system.unlock_beta_tester_mode()
            self.beta_tester_unlocked = True

        # Start System Architect Mode - become ARCHON
        self.start_architect_mode()

    def start_beta_tester_mode(self):
        """Start Ryan Carver Beta Tester Mode"""
        print("=== RYAN CARVER BETA TESTER MODE ACTIVATED ===")

        self.beta_tester_mode = True
        self.state = "beta_tester"
        self.player_frozen = False

        # Give infinite dashes
        self.player.max_dash_charges = 999
        self.player.dash_charges = 999

        # Reset to corrupted Level 1
        self.load_level(1)

        # Apply corruption visual effects
        self.effects.trigger_glitch(5.0, 5)  # Continuous glitch

        # Play corrupted music (level 3 music for intensity)
        self.audio.play_music("level3", fade_ms=2000)

    def start_architect_mode(self):
        """Start System Architect Mode - become ARCHON"""
        print("=== SYSTEM ARCHITECT MODE ACTIVATED ===")

        self.state = "architect"
        self.player_frozen = True
        self.architect_mode.start()

        # Play atmospheric music (level 3 music for epicness)
        self.audio.play_music("level3", fade_ms=2000)

    # ------------------------------------------------------------
    def draw_game_over(self):
        """Draw the game over screen overlay"""
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Game Over Text
        font_large = pygame.font.Font(None, 120)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        font_tiny = pygame.font.Font(None, 24)

        # Main title with glitch effect
        glitch_offset = int(self.game_over_timer * 10) % 4
        title = font_large.render("SYSTEM FAILURE", True, (255, 50, 50))
        title_rect = title.get_rect(center=(WIDTH // 2 + glitch_offset, HEIGHT // 2 - 140))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = font_medium.render("CONNECTION LOST", True, (0, 255, 255))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(subtitle, subtitle_rect)

        # Show chaos mode score if applicable
        if self.chaos_mode and hasattr(self, 'chaos_mode'):
            score_text = font_medium.render(f"FINAL SCORE: {self.chaos_mode.score}", True, (255, 50, 255))
            score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(score_text, score_rect)

            if self.chaos_mode.high_score > 0:
                high_text = font_small.render(f"High Score: {self.chaos_mode.high_score}", True, (150, 150, 255))
                high_rect = high_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
                self.screen.blit(high_text, high_rect)

        # Instructions - NO chaos mode option on game over
        y_start = HEIGHT // 2 + 100
        instruction1 = font_small.render("R - Restart  |  ESC - Quit", True, (200, 200, 200))
        instruction1_rect = instruction1.get_rect(center=(WIDTH // 2, y_start))
        self.screen.blit(instruction1, instruction1_rect)

    def draw_victory(self):
        """Draw the victory screen overlay"""
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Victory Text
        font_large = pygame.font.Font(None, 100)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)

        # Main title with cyan glow
        title = font_large.render("ARCHON DEFEATED", True, (0, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = font_medium.render("SIMULATION STABILIZED", True, (50, 255, 50))
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
        self.screen.blit(subtitle, subtitle_rect)

        # Final message
        message = font_small.render("Did you save them, or just yourself?", True, (200, 200, 200))
        message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(message, message_rect)

        # Chaos mode unlock message
        unlock_msg = font_small.render("CHAOS MODE UNLOCKED", True, (255, 50, 255))
        unlock_rect = unlock_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(unlock_msg, unlock_rect)

        # Instructions
        instruction = font_small.render("R - Restart  |  C - Chaos Mode  |  ESC - Quit", True, (150, 150, 150))
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        self.screen.blit(instruction, instruction_rect)
