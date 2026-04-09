# src/core/save_system.py
import json
import os
from datetime import datetime


class SaveSystem:
    """Handles saving and loading game progress and unlocks"""

    def __init__(self, save_file="save_data.json"):
        self.save_file = save_file
        self.data = {
            "beta_tester_unlocked": False,
            "perfect_run_completed": False,
            "tutorial_completed": False,  # Track if player has completed tutorial once
            "timestamp": None,
            "highscores": {},
            "easter_eggs_collected": [],  # List of collected easter eggs ["level1", "level2", "level3"]
            "best_times": {},  # Best times for each level {"level1": 45.2, "level2": 67.8, etc.}
            "total_best_time": None  # Best time for full game completion
        }
        self.load()

    def load(self):
        """Load save data from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.data = json.load(f)
                print(f"Save data loaded from {self.save_file}")
            except Exception as e:
                print(f"Error loading save data: {e}")
                # Use default data if load fails
        else:
            print("No save file found, using defaults")

    def save(self):
        """Save data to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            print(f"Save data written to {self.save_file}")
        except Exception as e:
            print(f"Error saving data: {e}")

    def unlock_beta_tester_mode(self):
        """Unlock Ryan Carver Beta Tester Mode"""
        self.data["beta_tester_unlocked"] = True
        self.data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save()
        print("RYAN CARVER BETA TESTER MODE UNLOCKED!")

    def is_beta_tester_unlocked(self):
        """Check if beta tester mode is unlocked"""
        return self.data.get("beta_tester_unlocked", False)

    def mark_perfect_run(self):
        """Mark that player completed a perfect run (no deaths)"""
        self.data["perfect_run_completed"] = True
        self.save()

    def set_highscore(self, mode, score):
        """Set highscore for a game mode"""
        if mode not in self.data["highscores"] or score > self.data["highscores"][mode]:
            self.data["highscores"][mode] = score
            self.save()
            return True  # New highscore
        return False

    def get_highscore(self, mode):
        """Get highscore for a game mode"""
        return self.data["highscores"].get(mode, 0)

    def mark_tutorial_completed(self):
        """Mark that player has completed the tutorial"""
        self.data["tutorial_completed"] = True
        self.save()

    def has_completed_tutorial(self):
        """Check if player has completed tutorial at least once"""
        return self.data.get("tutorial_completed", False)

    def collect_easter_egg(self, level_name):
        """Mark an easter egg as collected"""
        if "easter_eggs_collected" not in self.data:
            self.data["easter_eggs_collected"] = []
        if level_name not in self.data["easter_eggs_collected"]:
            self.data["easter_eggs_collected"].append(level_name)
            self.save()
            return True  # New collection
        return False  # Already collected

    def is_easter_egg_collected(self, level_name):
        """Check if easter egg for a level is collected"""
        return level_name in self.data.get("easter_eggs_collected", [])

    def get_easter_egg_count(self):
        """Get number of easter eggs collected"""
        return len(self.data.get("easter_eggs_collected", []))

    def save_best_time(self, level_name, time):
        """Save best time for a level if it's better than existing"""
        if "best_times" not in self.data:
            self.data["best_times"] = {}

        if level_name not in self.data["best_times"] or time < self.data["best_times"][level_name]:
            self.data["best_times"][level_name] = time
            self.save()
            return True  # New record
        return False

    def get_best_time(self, level_name):
        """Get best time for a level"""
        return self.data.get("best_times", {}).get(level_name, None)

    def save_total_best_time(self, time):
        """Save total game best time"""
        if self.data.get("total_best_time") is None or time < self.data["total_best_time"]:
            self.data["total_best_time"] = time
            self.save()
            return True  # New record
        return False

    def get_total_best_time(self):
        """Get total game best time"""
        return self.data.get("total_best_time", None)
