"""
entities/ai_car.py

AI-controlled car.

This class inherits from Car and receives a prebuilt action dictionary from
the AI controller. This keeps decision-making separate from movement logic.

That separation is useful because:
- ai_controller.py decides what the AI wants to do
- ai_car.py applies those decisions using the same rules as a normal car
"""

from __future__ import annotations

import config
from entities.car import Car


class AICar(Car):
    """
    Car controlled by the AI system.
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x,
            y=y,
            body_color=config.AI_CAR_BODY_COLOR,
            nose_color=config.AI_CAR_NOSE_COLOR,
        )

    def update_from_actions(self, actions: dict[str, bool]) -> None:
        """
        Apply the AI-generated action dictionary through the shared car update.
        """
        self.update(
            accelerate=actions.get("accelerate", False),
            reverse=actions.get("reverse", False),
            turn_left=actions.get("turn_left", False),
            turn_right=actions.get("turn_right", False),
            boost=actions.get("boost", False),
        )