# Echo Runner

## Story
You are the lead engineer who built this simulation. Your consciousness was uploaded to test it when the system (ARCHON) began to destabilize. The world is splitting into phases as corruption spreads. You must navigate through increasingly unstable sectors to reach and confront the ARCHON core - which you discover is your own control layer.

## Gameplay Features

### Core Mechanics
- **Movement**: A/D or Arrow Keys to move left/right
- **Jump**: SPACE/W/UP to jump
- **Dash**: SHIFT to dash (consumes energy charge, leaves neon trail)
- **Lives**: Start with 3 lives, take damage from enemies
- **Energy**: 5 dash charges that regenerate or can be restored with pickups

### Power-ups
- **Energy Drink** (Monster Can): Restores all dash charges
- **Speed Boost** (Lightning): 3 seconds of increased movement speed
- **Life Restore** (Heart): Restores 1 life if below maximum

### Enemies
- **Security Drones**: Patrol and chase when you get close
- **ARCHON Boss** (Level 3): Multi-phase final boss with projectile attacks

### Levels
1. **Clean Sim / Neon District**: Stable system, basic enemies
2. **Corrupt Sector**: Visual glitches, more enemies, industrial theme
3. **ARCHON Core**: Maximum corruption, boss battle

### Special Features
- **Glitch Terminals**: Interact to reveal lore about the simulation
- **Screen Effects**: Shake, glitch, and corruption effects
- **Dynamic Backgrounds**: Parallax scrolling that changes per level
- **Neon Trail System**: Visual dash trails with particle effects

## Setup Instructions

### Requirements
```bash
pip install pygame
```

### Running the Game
```bash
python main.py
```

### File Structure
```
echo_runner/
├── main.py              # Entry point
├── settings.py          # Game configuration
├── assets/              # Graphics and sounds
│   ├── characters/      # Player and enemy sprites
│   ├── items/          # Pickup sprites
│   └── bg/             # Background layers for each level
├── src/
│   ├── core/           # Game logic
│   ├── entities/       # Player, enemies, items, boss
│   ├── systems/        # Effects, HUD, sound
│   └── world/          # Platforms, camera
└── data/
    └── levels/         # Level JSON files
```

## Controls Summary
- **Move**: A/D or Left/Right Arrows
- **Jump**: Space/W/Up Arrow
- **Dash**: Left Shift
- **Pause**: ESC (when implemented)

## Tips
- Use dash to pass through enemies (damages boss)
- Collect power-ups to survive longer
- Watch the stability meter - it increases over time
- Each level gets progressively harder with more enemies
- The ARCHON boss has 3 phases with different attack patterns

## Development Status
### Implemented (✅)
- Player movement, jumping, dashing
- Enemy AI with chase behavior
- Multiple item types with effects
- Level progression system
- ARCHON boss battle
- Visual effects system
- Parallax backgrounds
- Platform collision
- HUD with health, energy, stability




---
*"The simulation is breaking. Your own creation turns against you. Run, fight, survive."*
