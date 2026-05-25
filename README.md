# I Wanna Be a CODER

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.0+-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macOS-lightgrey.svg)

**I Wanna Be a CODER** is a 2D platformer game developed in Python using Pygame. The game features two distinct level types (runner and platformer), a challenging boss battle, save/load system, and dynamic difficulty scaling based on player performance.

## Game Features

- **Two Level Types**: 
  - First level: Auto-scrolling runner with door choices affecting score
  - Second level: Traditional platformer with enemies, shooting mechanics, and collectible coins
- **Dynamic Boss Battle**: Difficulty adjusts based on player's performance in previous levels
- **Save System**: Store and load results from 12 save slots
- **Interactive UI**: Main menu, rules screens, death/victory screens, and ending credits
- **Audio System**: Background music and sound effects with channel management
- **Camera System**: Smooth camera following in platformer levels

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Pygame library

### Installation

```
# Clone the repository
git clone https://github.com/yourusername/i-wanna-be-a-coder.git
cd i-wanna-be-a-coder

# Install dependencies
pip install pygame
```

### Running the Game

```
python main.py
```

## Game Structure

### Directory Layout

```
game_data/
├── sprites/          # Game graphics (PNG files)
├── levels/           # Level files (.txt format)
├── music/            # Background music (MP3 files)
├── sound/            # Sound effects (WAV files)
├── font/             # Custom fonts (OTF files)
└── saves.txt         # Save data storage
```

### Level File Format

Levels are represented as text files where each character represents a tile type:

| Symbol | Tile Type |
|--------|-----------|
| `#` | Wall |
| `!` | Vertical spike (pointing down) |
| `?` | Vertical spike (pointing up) |
| `=` | Horizontal spike (pointing right) |
| `-` | Horizontal spike (pointing left) |
| `$` | Right door (adds score) |
| `%` | Wrong door (subtracts score) |
| `w` | Win gate |
| `*` | Coin |
| `&` | Boss lever |
| `s` | Saw |
| `@` | Player spawn |
| `9` | Enemy (shoots left) |
| `8` | Enemy (shoots right) |
| `B` | Boss spawn |

## Core Mechanics

### Player Controls

| Action | Key |
|--------|-----|
| Move Left | A |
| Move Right | D |
| Jump | Space |
| Shoot | Left Mouse Button |
| Interact (with lever) | E |

### Gameplay Systems

1. **First Level (Runner)**:
   - Auto-scrolling horizontal movement
   - Player controls vertical positioning with W/S keys
   - Choose doors to affect final score

2. **Second Level (Platformer)**:
   - Full movement with gravity and jumping
   - Shoot enemies (5 hits to defeat)
   - Collect coins (+5 points each)
   - Avoid spikes, saws, and enemy projectiles

3. **Boss Battle**:
   - Activates after completing both levels
   - Difficulty (easy/normal/hard) determined by:
     - First level score (above 1 = easy, below -1 = hard)
     - Second level score (above 15 = +health, below 0 = -health)
   - Boss attacks: Thunder strikes, circular saws, bullet barrages

### Scoring System

- **First Level**: Score changes based on door choices (right door: +1, wrong door: -1)
- **Second Level**: Start with 30 points, -1 on death, +5 per coin
- **Boss Health**: 2 base HP, modified by second level performance

## Code Architecture

### Main Classes

| Class | Description |
|-------|-------------|
| `Player` | Character control, collision, shooting, damage handling |
| `Camera` | Viewport following for platformer levels |
| `Boss` | Boss logic with multiple attack patterns and HP management |
| `Enemy` | Stationary turret enemies with shooting patterns |
| `Tile` | Static level geometry (walls, spikes, doors) |
| `Shoot` | Projectiles from player and enemies |
| `AnimatedSprite` | Frame-based animations for coins, effects, saws |
| `Button` | UI buttons with hover/click states |
| `Sound_Control` | Centralized audio management with multiple channels |

### Sprite Groups

The game uses Pygame's `sprite.Group` for efficient object management:

- `ALL_SPRITES`: All renderable objects
- `TILES_GROUP`: Solid collision geometry
- `DEADLY_TILES_GROUP`: Hazards that damage player
- `ENEMY_GROUP`: Enemy units
- `PLAYER_SHOOT_GROUP`: Player projectiles
- `SHOOT_GROUP`: Enemy projectiles
- `BONUS_SPRITES`: Collectibles
- `EFFECTS`: Explosion animations
- `ATTACK`: Boss attack objects

### Collision System

- Uses `pygame.sprite.collide_mask()` for pixel-perfect collision
- Separate horizontal and vertical collision handling with position correction
- Invincibility frames after taking damage (105 frames)

## Save System

The game supports saving and loading results from 12 slots:
- Stores first level score (or "???" if incomplete)
- Stores second level score (or "???" if incomplete)
- Data persists in `game_data/saves.txt`

Save format example:
```
15;42
-2;???
???;18
```

## Audio Management

The `Sound_Control` class manages:
- 4 audio channels (SFX, explosions, enemy sounds, boss attacks)
- Dynamic background music switching between menu, levels, and boss fight
- Volume balancing for different sound types

## State Management

Game states are controlled by the `LEVEL` global variable:
- `'menu'` - Main menu
- `'save'` - Save/Load screen
- `'first'` - Runner level
- `'second'` - Platformer level
- `'boss_but'` - Boss entrance room
- `'boss_arena'` - Boss fight

## Development Notes

### Global Variables

The code uses several global variables for state management. While not ideal, they were necessary given the project scope. Key globals include:
- `LEVEL`, `PLAYER`, `CAMERA` - Core game state
- `FIRST_SCORE`, `SECOND_SCORE` - Progress tracking
- `left`, `right`, `up` - Movement flags
- `DIFF`, `HEALTH` - Boss difficulty parameters

### Extending the Game

To add new level types:
1. Create a new level file in `game_data/levels/`
2. Add level symbol mappings in `generate_level()`
3. Implement level-specific logic in `Player.update()`

To add new enemy types:
1. Create sprite assets
2. Extend `TILE_IMAGES` dictionary
3. Add symbol handler in `generate_level()`

Authors
-------
### Developer
- [Simonov Maksim](https://github.com/UuAcC)
### Supervisor
- Alexandr Popov

Developed as a course project demonstrating game development concepts in Python using Pygame.


---
**Note**: All game assets (sprites, music, sound effects) are property of their respective owners and should be replaced with original content for distribution.
