# src/systems/sound_manager.py
import pygame
import os


class SoundManager:
    """Manages sound effects for the game"""
    
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.enabled = True
        self.volume = 0.5
        
        # Since we don't have actual sound files, we'll create simple
        # sound effects programmatically
        self.create_synthetic_sounds()
        
    def create_synthetic_sounds(self):
        """Create synthetic sound effects"""
        # We'll use pygame's built-in sound generation capabilities
        # For now, this is a placeholder that would generate beeps/boops
        pass
        
    def play(self, sound_name):
        """Play a sound effect"""
        if not self.enabled:
            return
            
        # For now, just print what sound would play
        # In a real implementation, you'd have:
        # if sound_name in self.sounds:
        #     self.sounds[sound_name].play()
        
        # Debug output
        if sound_name == "dash":
            print("*WHOOSH*")
        elif sound_name == "pickup":
            print("*BLING*")
        elif sound_name == "damage":
            print("*ZAP*")
        elif sound_name == "jump":
            print("*BOING*")
        elif sound_name == "explosion":
            print("*BOOM*")
            
    def set_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        
    def toggle(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        return self.enabled
