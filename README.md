# Tetris 80s Plus

A modern Python implementation of classic Tetris with an 80s-inspired visual style and experimental gameplay mechanics, built as a standalone desktop application using Tkinter.

This project started as a technical and creative exercise and evolved into a fully playable game that explores geometric transformations, real-time event loops, and simple game engine design in Python.

---

## What does this project do?

**Tetris 80s Plus** is a playable Tetris game with several non-standard features:

- Classic Tetris gameplay on a 10×20 board
- Retro 80s-style ASCII-inspired visuals
- Dynamic falling speed (including randomly spawning fast-fall pieces)
- Optional horizontal mirroring of pieces
- Scoring based on cleared lines
- Sound effects (with cross-platform fallback)

The project demonstrates how a complete interactive application can be built using only Python’s standard library.

---

## Gameplay features

- **Standard movement**: left / right / soft drop
- **Rotation with wall-kick logic**
- **Hard drop**
- **Mirrored pieces** (toggle during gameplay)
- **Fast mode pieces** that fall significantly faster
- **Line clearing and scoring**
- **Game over and restart support**

Controls:
- ← / → : Move piece
- ↓ : Soft drop
- ↑ : Rotate
- Space : Hard drop
- M : Toggle mirror mode
- S : Toggle sound
- R : Restart game

---

## Input and Output

### Input
- Keyboard input only
- No external data files required

### Output
- A graphical game window rendered using Tkinter
- Real-time visual feedback and score display
- Optional sound feedback

---

## Technical overview

- Language: **Python 3**
- GUI: **Tkinter**
- Sound:
  - `winsound` on Windows
  - Tkinter bell as a fallback on macOS/Linux
- No third-party dependencies

Key technical aspects include:
- Board representation using a 2D list
- Shape generation via mathematical rotation and mirroring in a 4×4 grid
- Collision detection and line clearing logic
- Event-driven architecture using Tkinter’s main loop and timed callbacks

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/tetris-80s-plus.git
cd tetris-80s-plus
```
Run it using python



