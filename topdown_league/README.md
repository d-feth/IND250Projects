# Top-Down League

Top-Down League is a 2D top-down car soccer game made in Python with pygame for a school final project.

The game is inspired by Rocket League, but adapted into a 2D top-down format with no height mechanics. The player controls a car and competes against an AI opponent to hit the ball into the opposing goal before time runs out.

## Features

- 2D top-down arena with recessed side goals
- Player-controlled car with acceleration, reverse, steering, and boost
- AI-controlled opponent
- Ball physics with wall collisions and car impacts
- Goal detection and score tracking
- Match timer
- Kickoff countdown after goals
- Timer starts after first touch on kickoff
- Main menu and pause menu
- Boost meter
- Boost trail visual effects
- Styled top-down car visuals
- Textured ball with scrolling surface effect

## Controls

- **W** = accelerate
- **S** = reverse
- **A** = turn left
- **D** = turn right
- **Left Shift** or **Space** = boost
- **ESC** = pause / resume
- **R** = restart match
- **M** = return to main menu from pause or result screen
- **Enter** = start game from main menu

## Requirements

- Python 3.x
- pygame-ce

Install pygame-ce with:

```bash
pip install -r requirements.txt