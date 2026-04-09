# src/core/audio_manager.py
import pygame
import os
import numpy as np
from src.core.utils import get_resource_path


class AudioManager:
    """Manages all music and sound effects for the game"""

    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Volume settings
        self.music_volume = 0.25  # 25% - faint background
        self.sfx_volume = 0.6     # 60% - louder gameplay sounds

        # Music tracks
        self.music_tracks = {}
        self.current_track = None
        self.load_music()

        # Sound effects
        self.sfx = {}
        self.generate_sound_effects()

        print("Audio Manager initialized")

    def load_music(self):
        """Load all music files"""
        music_dir = "assets/music/"

        # Define music file names
        music_files = {
            "intro": "intro_music.ogg",
            "level1": "level1_music.ogg",
            "level2": "level2_music.ogg",
            "level3": "level3_music.ogg",
        }

        for name, filename in music_files.items():
            path = os.path.join(music_dir, filename)
            abs_path = get_resource_path(path)
            if os.path.exists(abs_path):
                self.music_tracks[name] = abs_path
                print(f"Loaded music: {name}")
            else:
                print(f"WARNING: Music file not found: {path}")

    def generate_sound_effects(self):
        """Generate procedural sound effects using pygame"""
        sample_rate = 22050

        # Jump sound - rising tone
        self.sfx["jump"] = self.generate_jump_sound(sample_rate)

        # Dash sound - quick whoosh
        self.sfx["dash"] = self.generate_dash_sound(sample_rate)

        # Land sound - thud
        self.sfx["land"] = self.generate_land_sound(sample_rate)

        # Drone explosion - buzz explosion
        self.sfx["drone_explode"] = self.generate_explosion_sound(sample_rate)

        # Item pickup - chime
        self.sfx["item_pickup"] = self.generate_pickup_sound(sample_rate)

        # Boss attack - aggressive buzz
        self.sfx["boss_attack"] = self.generate_boss_attack_sound(sample_rate)

        # Boss defeat - epic explosion
        self.sfx["boss_defeat"] = self.generate_boss_defeat_sound(sample_rate)

        # Menu beep - simple tone
        self.sfx["menu_beep"] = self.generate_menu_beep(sample_rate)

        # Menu select - confirmation tone
        self.sfx["menu_select"] = self.generate_menu_select(sample_rate)

        # Player death - descending glitch sound
        self.sfx["player_death"] = self.generate_death_sound(sample_rate)

        print(f"Generated {len(self.sfx)} procedural sound effects")

    def generate_jump_sound(self, sample_rate):
        """Generate a rising jump sound"""
        duration = 0.15
        samples = int(sample_rate * duration)

        # Rising frequency from 200Hz to 400Hz
        t = np.linspace(0, duration, samples)
        frequency = np.linspace(200, 400, samples)
        wave = np.sin(2 * np.pi * frequency * t)

        # Apply envelope (fade out)
        envelope = np.linspace(1, 0, samples)
        wave = wave * envelope

        # Convert to 16-bit audio
        wave = np.int16(wave * 32767 * self.sfx_volume)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_dash_sound(self, sample_rate):
        """Generate a quick whoosh sound"""
        duration = 0.1
        samples = int(sample_rate * duration)

        # Noise-based whoosh
        wave = np.random.uniform(-1, 1, samples)

        # Apply bandpass effect (keep mid frequencies)
        t = np.linspace(0, duration, samples)
        modulation = np.sin(2 * np.pi * 300 * t)
        wave = wave * modulation

        # Apply envelope - ensure it matches wave length
        third = samples // 3
        envelope = np.concatenate([
            np.linspace(0, 1, third),
            np.linspace(1, 0, samples - third)
        ])
        # Ensure envelope length matches wave
        if len(envelope) != len(wave):
            envelope = envelope[:len(wave)]
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.5)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_land_sound(self, sample_rate):
        """Generate a thud landing sound"""
        duration = 0.08
        samples = int(sample_rate * duration)

        # Low frequency thud (80Hz)
        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * 80 * t)

        # Add some noise for texture
        noise = np.random.uniform(-0.3, 0.3, samples)
        wave = wave + noise

        # Quick decay envelope
        envelope = np.exp(-10 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.6)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_explosion_sound(self, sample_rate):
        """Generate drone explosion sound"""
        duration = 0.3
        samples = int(sample_rate * duration)

        # Start with noise
        wave = np.random.uniform(-1, 1, samples)

        # Add low frequency rumble
        t = np.linspace(0, duration, samples)
        rumble = np.sin(2 * np.pi * 60 * t) * 0.5
        wave = wave * 0.5 + rumble

        # Exponential decay
        envelope = np.exp(-8 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.7)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_pickup_sound(self, sample_rate):
        """Generate item pickup chime"""
        duration = 0.2
        samples = int(sample_rate * duration)

        # Arpeggio: C5, E5, G5 (523, 659, 784 Hz)
        t = np.linspace(0, duration, samples)

        # Three notes in sequence
        segment = samples // 3
        freq1 = np.sin(2 * np.pi * 523 * t[:segment])
        freq2 = np.sin(2 * np.pi * 659 * t[segment:2*segment])
        freq3 = np.sin(2 * np.pi * 784 * t[2*segment:samples])

        wave = np.concatenate([freq1, freq2, freq3])

        # Smooth envelope - use actual wave length
        t_wave = np.linspace(0, duration, len(wave))
        envelope = np.exp(-3 * t_wave)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.5)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_boss_attack_sound(self, sample_rate):
        """Generate aggressive boss attack sound"""
        duration = 0.25
        samples = int(sample_rate * duration)

        # Low aggressive buzz
        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * 150 * t)

        # Add distortion
        wave = np.clip(wave * 2, -1, 1)

        # Add high frequency sizzle
        sizzle = np.sin(2 * np.pi * 2000 * t) * 0.3
        wave = wave + sizzle

        # Sharp attack, quick decay
        envelope = np.exp(-6 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.8)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_boss_defeat_sound(self, sample_rate):
        """Generate epic boss defeat explosion"""
        duration = 1.0
        samples = int(sample_rate * duration)

        # Heavy noise explosion
        wave = np.random.uniform(-1, 1, samples)

        # Add rumble at different frequencies
        t = np.linspace(0, duration, samples)
        rumble1 = np.sin(2 * np.pi * 40 * t) * 0.4
        rumble2 = np.sin(2 * np.pi * 70 * t) * 0.3
        wave = wave * 0.4 + rumble1 + rumble2

        # Long decay
        envelope = np.exp(-2 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_menu_beep(self, sample_rate):
        """Generate menu navigation beep"""
        duration = 0.05
        samples = int(sample_rate * duration)

        # Simple 800Hz beep
        t = np.linspace(0, duration, samples)
        wave = np.sin(2 * np.pi * 800 * t)

        # Quick envelope
        envelope = np.exp(-20 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.4)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_menu_select(self, sample_rate):
        """Generate menu selection confirmation"""
        duration = 0.15
        samples = int(sample_rate * duration)

        # Two-tone confirmation (600Hz -> 800Hz)
        t = np.linspace(0, duration, samples)
        half = samples // 2

        tone1 = np.sin(2 * np.pi * 600 * t[:half])
        tone2 = np.sin(2 * np.pi * 800 * t[half:samples])
        wave = np.concatenate([tone1, tone2])

        # Smooth envelope - use actual wave length
        t_wave = np.linspace(0, duration, len(wave))
        envelope = np.exp(-8 * t_wave)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.5)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def generate_death_sound(self, sample_rate):
        """Generate player death sound - descending glitchy tone"""
        duration = 0.5
        samples = int(sample_rate * duration)

        # Descending frequency from 400Hz to 80Hz (falling pitch)
        t = np.linspace(0, duration, samples)
        frequency = np.linspace(400, 80, samples)
        wave = np.sin(2 * np.pi * frequency * t)

        # Add digital glitch distortion
        glitch_noise = np.random.uniform(-0.3, 0.3, samples)
        wave = wave + glitch_noise

        # Add low rumble
        rumble = np.sin(2 * np.pi * 60 * t) * 0.4
        wave = wave * 0.7 + rumble

        # Exponential decay envelope
        envelope = np.exp(-2.5 * t)
        wave = wave * envelope

        wave = np.int16(wave * 32767 * self.sfx_volume * 0.8)
        stereo_wave = np.column_stack((wave, wave))

        return pygame.sndarray.make_sound(stereo_wave)

    def play_music(self, track_name, fade_ms=2000):
        """Play a music track with fade-in"""
        if track_name not in self.music_tracks:
            print(f"WARNING: Music track '{track_name}' not found")
            return

        # Don't restart if already playing this track
        if self.current_track == track_name and pygame.mixer.music.get_busy():
            return

        # Stop current music
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(1000)  # 1 second fade out
            pygame.time.wait(1000)  # Wait for fade out

        # Load and play new track
        pygame.mixer.music.load(self.music_tracks[track_name])
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1, fade_ms=fade_ms)  # Loop indefinitely with fade-in

        self.current_track = track_name
        print(f"Playing music: {track_name} (fade-in: {fade_ms}ms)")

    def stop_music(self, fade_ms=1000):
        """Stop the current music with fade-out"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
            self.current_track = None

    def play_sfx(self, sfx_name):
        """Play a sound effect"""
        if sfx_name in self.sfx:
            self.sfx[sfx_name].play()
        else:
            print(f"WARNING: Sound effect '{sfx_name}' not found")

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Note: Would need to regenerate sounds to apply new volume
