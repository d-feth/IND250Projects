"""
systems/input_handler.py

This file converts raw keyboard state into a clean action dictionary.

Why do this?
Because it keeps the rest of the game from directly depending on
specific keyboard key constants all over the code.

That makes it easier later to:
- support multiple players
- remap controls
- add controllers
- keep input logic organized
"""

from __future__ import annotations

import pygame


def get_player1_actions(keys: pygame.key.ScancodeWrapper) -> dict[str, bool]:
    """
    Convert current keyboard state into a dictionary of player 1 actions.

    Controls:
    - W = accelerate
    - S = reverse
    - A = turn left
    - D = turn right
    - Left Shift or Space = boost
    """
    return {
        "accelerate": keys[pygame.K_w],
        "reverse": keys[pygame.K_s],
        "turn_left": keys[pygame.K_a],
        "turn_right": keys[pygame.K_d],
        "boost": keys[pygame.K_LSHIFT] or keys[pygame.K_SPACE],
    }


# Backward-compatible alias so older code won't break if referenced.
def get_player_actions(keys: pygame.key.ScancodeWrapper) -> dict[str, bool]:
    """
    Alias for player 1 controls.
    """
    return get_player1_actions(keys)