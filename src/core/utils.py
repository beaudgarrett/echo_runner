# src/core/utils.py
import pygame
import os
import sys


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_image(path):
    # Convert to absolute path for PyInstaller compatibility
    abs_path = get_resource_path(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Image not found: {path} (looked in {abs_path})")
    return pygame.image.load(abs_path).convert_alpha()


def slice_spritesheet(path, frame_w, frame_h):
    image = load_image(path)
    sheet_w, sheet_h = image.get_size()
    frames = []
    for y in range(0, sheet_h, frame_h):
        for x in range(0, sheet_w, frame_w):
            frame = image.subsurface(pygame.Rect(x, y, frame_w, frame_h)).copy()
            frames.append(frame)
    return frames
