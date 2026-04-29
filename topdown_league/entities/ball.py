"""
entities/ball.py

Ball entity for the top-down car soccer game.

Responsibilities:
- store position and velocity
- apply friction
- limit speed
- draw the ball
- animate a simple top-down scrolling texture
- reset the ball to center field
"""

from __future__ import annotations

import math
import pygame

import config
from utils import limit_vector


class Ball:
    """
    Represents the game ball.
    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0

        self.radius = config.BALL_RADIUS
        self.friction = config.BALL_FRICTION
        self.max_speed = config.BALL_MAX_SPEED

        # Texture scroll offsets for top-down motion
        self.texture_scroll_x = 0.0
        self.texture_scroll_y = 0.0

    def reset(self, x: float, y: float) -> None:
        """
        Reset the ball to a known position with no velocity.
        """
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.texture_scroll_x = 0.0
        self.texture_scroll_y = 0.0

    def update(self) -> None:
        """
        Update the ball for one frame.
        """
        self.x += self.vx
        self.y += self.vy

        # Scroll the visible texture in the direction the ball is moving.
        # This reads better from a top-down perspective than simple rotation.
        self.texture_scroll_x += self.vx * 1.4
        self.texture_scroll_y += self.vy * 1.4

        self.vx *= self.friction
        self.vy *= self.friction

        self.vx, self.vy = limit_vector(self.vx, self.vy, self.max_speed)

        if abs(self.vx) < 0.02:
            self.vx = 0.0
        if abs(self.vy) < 0.02:
            self.vy = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the ball with a gray textured look and a scrolling texture effect.
        """
        diameter = self.radius * 2
        ball_surface = pygame.Surface((diameter + 4, diameter + 4), pygame.SRCALPHA)
        center_x = self.radius + 2
        center_y = self.radius + 2
        center = (center_x, center_y)

        # Base circle
        pygame.draw.circle(ball_surface, config.BALL_BASE_COLOR, center, self.radius)
        pygame.draw.circle(ball_surface, config.BALL_OUTLINE_COLOR, center, self.radius, width=2)

        # Patch system:
        # We define a set of local patch centers and scroll them in the direction
        # of motion. To simulate continuity, we also draw wrapped copies.
        patch_radius = max(4, int(self.radius * 0.18))
        wrap_span = self.radius * 1.55

        base_patches = [
            (-self.radius * 0.35, -self.radius * 0.28),
            (self.radius * 0.28, -self.radius * 0.18),
            (-self.radius * 0.10, 0),
            (self.radius * 0.34, self.radius * 0.24),
            (-self.radius * 0.30, self.radius * 0.30),
        ]

        scroll_x = self.texture_scroll_x % wrap_span
        scroll_y = self.texture_scroll_y % wrap_span

        for base_x, base_y in base_patches:
            for wrap_x in (-wrap_span, 0, wrap_span):
                for wrap_y in (-wrap_span, 0, wrap_span):
                    px = center_x + base_x + scroll_x + wrap_x - wrap_span / 2
                    py = center_y + base_y + scroll_y + wrap_y - wrap_span / 2

                    # Only draw patches whose centers are within the ball
                    dx = px - center_x
                    dy = py - center_y
                    if math.hypot(dx, dy) <= self.radius - patch_radius * 0.5:
                        pygame.draw.circle(
                            ball_surface,
                            config.BALL_PATCH_COLOR,
                            (int(px), int(py)),
                            patch_radius,
                        )

        # Small highlight
        highlight_center = (
            int(center_x - self.radius * 0.35),
            int(center_y - self.radius * 0.35),
        )
        pygame.draw.circle(
            ball_surface,
            config.BALL_HIGHLIGHT_COLOR,
            highlight_center,
            max(3, int(self.radius * 0.16)),
        )

        surface.blit(
            ball_surface,
            (int(self.x - self.radius - 2), int(self.y - self.radius - 2)),
        )