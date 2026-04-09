# src/systems/background_manager.py
import os
import pygame
from settings import WIDTH, HEIGHT
from src.core.utils import get_resource_path


class BackgroundManager:
    def __init__(self):
        self.layers = []
        self.camera_x = 0
        self.width = WIDTH

    def set_level(self, level_index: int):
        folder = f"assets/bg/level{level_index}"
        abs_folder = get_resource_path(folder)
        self.layers = []

        if not os.path.exists(abs_folder):
            print(f"[BG] WARNING: Missing folder {folder}")
            return

        for filename in sorted(os.listdir(abs_folder)):
            if filename.lower().endswith(".png"):
                path = os.path.join(abs_folder, filename)
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                self.layers.append(img)

        self.width = WIDTH
        print(f"[BG] Loaded {len(self.layers)} layers for Level {level_index}")

    def update(self, dx):
        # we’re tying background to camera_x, so we don’t need dx here
        pass

    def draw(self, screen: pygame.Surface):
        screen_w = screen.get_width()
        for i, layer in enumerate(self.layers):
            depth = 0.25 + i * 0.09
            offset_x = -self.camera_x * depth
            lw = layer.get_width()
            for x in range(-1, screen_w // lw + 2):
                screen.blit(layer, (offset_x + x * lw, 0))
