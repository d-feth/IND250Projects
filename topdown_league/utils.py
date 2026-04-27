"""
utils.py

Small helper functions used across the project.

Important note:
This file should contain reusable utility logic, not random gameplay code.
If a function is specifically about cars, the ball, collisions, scoring, etc.,
it should usually live in the file that owns that system.
"""

from __future__ import annotations

import math
import pygame


def clamp(value: float, minimum: float, maximum: float) -> float:
    """
    Restrict a numeric value to a given range.

    Example:
    clamp(12, 0, 10) -> 10
    clamp(-3, 0, 10) -> 0
    """
    return max(minimum, min(value, maximum))


def magnitude(x: float, y: float) -> float:
    """
    Return the length of a 2D vector.
    """
    return math.hypot(x, y)


def limit_vector(x: float, y: float, max_length: float) -> tuple[float, float]:
    """
    Limit a 2D vector so its magnitude does not exceed max_length.

    This is useful for capping car speed while still preserving direction.
    """
    length = magnitude(x, y)

    if length == 0 or length <= max_length:
        return x, y

    scale = max_length / length
    return x * scale, y * scale


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    x: int,
    y: int,
    shadow: bool = False,
    shadow_color: tuple[int, int, int] = (0, 0, 0),
) -> None:
    """
    Draw text at a top-left position.

    Optional shadow makes HUD text easier to read against the field.
    """
    if shadow:
        shadow_surface = font.render(text, True, shadow_color)
        surface.blit(shadow_surface, (x + 2, y + 2))

    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


def draw_centered_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    center_x: int,
    center_y: int,
) -> None:
    """
    Draw text centered around a given position.
    """
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, rect)