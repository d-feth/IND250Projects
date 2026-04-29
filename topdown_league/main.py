"""
main.py

Entry point for the top-down car soccer project.

This file should stay small. Its job is to:
1. Initialize pygame
2. Initialize audio
3. Create the main Game object
4. Start the game loop
5. Quit pygame cleanly when the loop ends
"""

import pygame
import config
from game import Game


def main() -> None:
    """Main entry point for the program."""
    # Pre-initialize mixer so generated sounds use known audio settings.
    pygame.mixer.pre_init(
        frequency=config.AUDIO_FREQUENCY,
        size=config.AUDIO_SIZE,
        channels=config.AUDIO_CHANNELS,
        buffer=config.AUDIO_BUFFER,
    )

    pygame.init()

    game = Game()
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()