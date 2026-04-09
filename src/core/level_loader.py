# src/core/level_loader.py
import json
import pygame
from src.world.tiles import Platform
from src.entities.enemy_drone import EnemyDrone
from src.entities.item import EnergyDrink, SpeedBoost, LifeRestore, EasterEgg
from src.entities.npc_terminal import GlitchTerminal
from src.entities.boss_archon import ARCHON
from src.core.utils import get_resource_path


class LevelLoader:
    def __init__(self, path: str):
        abs_path = get_resource_path(path)
        with open(abs_path, "r") as f:
            self.data = json.load(f)

    def build(self, player_ref):
        bg_name = self.data.get("background", "level1")
        world_width = self.data.get("world_width", 4000)

        platforms = pygame.sprite.Group()
        drones = pygame.sprite.Group()
        items = pygame.sprite.Group()
        npcs = pygame.sprite.Group()

        # platforms
        for p in self.data.get("platforms", []):
            plat = Platform(p["x"], p["y"], p.get("width", 200))
            platforms.add(plat)

        # drones
        for d in self.data.get("drone_spawns", []):
            drone = EnemyDrone((d["x"], d["y"]))
            drone.set_player(player_ref)
            drones.add(drone)

        # items
        for it in self.data.get("items", []):
            if it["type"] == "EnergyDrink":
                item = EnergyDrink((it["x"], it["y"]))
                items.add(item)
            elif it["type"] == "SpeedBoost":
                item = SpeedBoost((it["x"], it["y"]))
                items.add(item)
            elif it["type"] == "LifeRestore":
                item = LifeRestore((it["x"], it["y"]))
                items.add(item)
            elif it["type"] == "EasterEgg":
                item = EasterEgg((it["x"], it["y"]))
                items.add(item)

        # npcs
        for n in self.data.get("npcs", []):
            if n["type"] == "GlitchTerminal":
                lore = n.get("lore", None)
                npc = GlitchTerminal((n["x"], n["y"]), lore_text=lore)
                npcs.add(npc)

        # boss (if present)
        boss = None
        if "boss" in self.data:
            boss_data = self.data["boss"]
            if boss_data["type"] == "ARCHON":
                boss = ARCHON((boss_data["x"], boss_data["y"]))
                boss.set_player(player_ref)

        return {
            "background": bg_name,
            "world_width": world_width,
            "platforms": platforms,
            "drones": drones,
            "items": items,
            "npcs": npcs,
            "boss": boss
        }
