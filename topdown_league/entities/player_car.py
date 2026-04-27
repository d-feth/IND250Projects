"""
entities/player_car.py

Player-controlled car.

This class inherits from Car and applies movement based on the action
dictionary returned by the input system.

Keeping the input translation here helps separate:
- raw keyboard reading (input_handler.py)
from
- how a player car responds to those actions
"""

from __future__ import annotations

from entities.car import Car


class PlayerCar(Car):
    """
    Car controlled by the player.
    """

    def update_from_actions(self, actions: dict[str, bool]) -> None:
        """
        Read the action dictionary and pass the appropriate booleans
        into the shared base-class update logic.
        """
        self.update(
            accelerate=actions.get("accelerate", False),
            reverse=actions.get("reverse", False),
            turn_left=actions.get("turn_left", False),
            turn_right=actions.get("turn_right", False),
            boost=actions.get("boost", False),
        )