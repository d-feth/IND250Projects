"""
entities/ball.py

Ball entity for the top-down car soccer game.

For Phase 2, this class is responsible for:
- storing position and velocity
- applying friction
- limiting ball speed
- drawing the ball
- resetting the ball to center field

At this stage, wall collision and car-ball collision are handled in the
collision system rather than inside this class. That keeps responsibilities
more separated.
"""

from __future__ import annotations

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

        self.color = config.BALL_COLOR
        self.outline_color = config.BALL_OUTLINE_COLOR

    def reset(self, x: float, y: float) -> None:
        """
        Reset the ball to a known position with no velocity.
        """
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

    def update(self) -> None:
        """
        Update the ball for one frame.

        The ball:
        - moves according to its velocity
        - slows down gradually due to friction
        - has its speed capped for stability
        """
        self.x += self.vx
        self.y += self.vy

        self.vx *= self.friction
        self.vy *= self.friction

        self.vx, self.vy = limit_vector(self.vx, self.vy, self.max_speed)

        # Tiny velocities are snapped to zero so the ball does not drift forever.
        if abs(self.vx) < 0.02:
            self.vx = 0.0
        if abs(self.vy) < 0.02:
            self.vy = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the ball as a simple filled circle with outline.
        """
        center = (int(self.x), int(self.y))

        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, self.outline_color, center, self.radius, width=2)

        # Small highlight to help the ball look a little less flat
        highlight_center = (int(self.x - self.radius * 0.35), int(self.y - self.radius * 0.35))
        pygame.draw.circle(surface, (255, 245, 200), highlight_center, max(2, self.radius // 4))