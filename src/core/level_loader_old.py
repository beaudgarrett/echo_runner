# src/core/level_loader.py
import json
import pygame
from src.world.tiles import Platform
from src.entities.enemy_drone import EnemyDrone
from src.entities.item import EnergyDrink
from src.entities.npc_terminal import GlitchTerminal


class LevelLoader:
    def __init__(self, path: str):
        with open(path, "r") as f:
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

        # npcs
        for n in self.data.get("npcs", []):
            if n["type"] == "GlitchTerminal":
                npc = GlitchTerminal((n["x"], n["y"]))
                npcs.add(npc)

        return {
            "background": bg_name,
            "world_width": world_width,
            "platforms": platforms,
            "drones": drones,
            "items": items,
            "npcs": npcs,
        }
