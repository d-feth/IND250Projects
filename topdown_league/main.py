"""
main.py

Entry point for the top-down car soccer project.

This file should stay small. Its job is to:
1. Initialize pygame
2. Create the main Game object
3. Start the game loop
4. Quit pygame cleanly when the loop ends
"""

import pygame
from game import Game


def main() -> None:
    """Main entry point for the program."""
    pygame.init()

    game = Game()
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()