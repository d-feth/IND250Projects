"""
entities/car.py

Base Car class.

This class stores the shared behavior for any car in the game, whether it is:
- player controlled
- AI controlled
- possibly another type later

Responsibilities:
- store position / velocity / angle
- apply movement physics
- apply friction
- keep the car inside the arena, including recessed goal pockets
- manage boost resource
- draw the car as a rotated shape
- expose a collision radius for simple physics interactions
"""

from __future__ import annotations

import math
import pygame

import config
from utils import limit_vector


class Car:
    """
    Base car class with shared movement, boost, and drawing behavior.
    """

    def __init__(
        self,
        x: float,
        y: float,
        body_color: tuple[int, int, int] = config.CAR_BODY_COLOR,
        nose_color: tuple[int, int, int] = config.CAR_NOSE_COLOR,
    ) -> None:
        self.x = x
        self.y = y

        self.vx = 0.0
        self.vy = 0.0

        # Angle convention:
        # 0 = up, 90 = right, 180/-180 = down, -90 = left
        self.angle = 0.0

        self.body_color = body_color
        self.nose_color = nose_color

        self.width = config.CAR_WIDTH
        self.height = config.CAR_HEIGHT

        self.acceleration = config.CAR_ACCELERATION
        self.reverse_acceleration = config.CAR_REVERSE_ACCELERATION
        self.max_speed = config.CAR_MAX_SPEED
        self.turn_speed = config.CAR_TURN_SPEED
        self.friction = config.CAR_FRICTION
        self.boost_multiplier = config.CAR_BOOST_MULTIPLIER
        self.collision_radius = config.CAR_COLLISION_RADIUS

        # Boost resource
        self.boost_amount = config.BOOST_MAX

    def reset(self, x: float, y: float, angle: float) -> None:
        """
        Reset the car to a known position and facing direction.
        """
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = angle
        self.boost_amount = config.BOOST_MAX

    def update(
        self,
        accelerate: bool,
        reverse: bool,
        turn_left: bool,
        turn_right: bool,
        boost: bool,
    ) -> None:
        """
        Update the car for one frame.

        Steps:
        1. steer
        2. build forward vector
        3. decide whether boost is really active
        4. apply acceleration
        5. recharge or drain boost
        6. apply friction
        7. limit speed
        8. move
        9. keep in bounds
        """
        if turn_left:
            self.angle -= self.turn_speed
        if turn_right:
            self.angle += self.turn_speed

        radians = math.radians(self.angle - 90)
        forward_x = math.cos(radians)
        forward_y = math.sin(radians)

        boost_active = (
            boost
            and accelerate
            and self.boost_amount >= config.BOOST_MIN_TO_ACTIVATE
        )

        current_acceleration = self.acceleration
        current_max_speed = self.max_speed

        if boost_active:
            current_acceleration *= self.boost_multiplier
            current_max_speed *= self.boost_multiplier
            self.boost_amount = max(0.0, self.boost_amount - config.BOOST_DRAIN_PER_FRAME)
        else:
            self.boost_amount = min(config.BOOST_MAX, self.boost_amount + config.BOOST_RECHARGE_PER_FRAME)

        if accelerate:
            self.vx += forward_x * current_acceleration
            self.vy += forward_y * current_acceleration

        if reverse:
            self.vx -= forward_x * self.reverse_acceleration
            self.vy -= forward_y * self.reverse_acceleration

        self.vx *= self.friction
        self.vy *= self.friction

        self.vx, self.vy = limit_vector(self.vx, self.vy, current_max_speed)

        self.x += self.vx
        self.y += self.vy

        self.keep_in_bounds()

    def keep_in_bounds(self) -> None:
        """
        Keep the car inside the arena, including recessed goal pockets.

        Important fix:
        The car is allowed to pass through the side opening into the goal pocket.
        Once inside the pocket, it should collide with the pocket's back wall and
        top/bottom pocket walls rather than being treated like it hit a flat side wall.
        """
        radius = self.collision_radius

        goal_top = (config.SCREEN_HEIGHT - config.GOAL_HEIGHT) // 2
        goal_bottom = goal_top + config.GOAL_HEIGHT

        main_left = config.FIELD_MARGIN + radius
        main_right = config.SCREEN_WIDTH - config.FIELD_MARGIN - radius
        top_bound = config.FIELD_MARGIN + radius
        bottom_bound = config.SCREEN_HEIGHT - config.FIELD_MARGIN - radius

        left_pocket_back = config.FIELD_MARGIN - config.GOAL_DEPTH + radius
        right_pocket_back = config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH - radius

        # Car is considered in a pocket if its center has passed through the goal mouth.
        in_left_pocket = self.x < config.FIELD_MARGIN and goal_top <= self.y <= goal_bottom
        in_right_pocket = self.x > config.SCREEN_WIDTH - config.FIELD_MARGIN and goal_top <= self.y <= goal_bottom

        # ----------------------------
        # Horizontal resolution
        # ----------------------------
        if in_left_pocket:
            # Back wall of left pocket
            if self.x < left_pocket_back:
                self.x = left_pocket_back
                self.vx = 0.0

            # Inner vertical line where pocket meets field should remain open while
            # the car is inside the valid goal mouth y-range, so no snap-out here.

        elif in_right_pocket:
            # Back wall of right pocket
            if self.x > right_pocket_back:
                self.x = right_pocket_back
                self.vx = 0.0

        else:
            # Normal main-field side walls apply only when not using the goal mouth
            goal_mouth_y = goal_top <= self.y <= goal_bottom

            if self.x < main_left and not goal_mouth_y:
                self.x = main_left
                self.vx = 0.0
            elif self.x > main_right and not goal_mouth_y:
                self.x = main_right
                self.vx = 0.0

        # ----------------------------
        # Vertical resolution
        # ----------------------------
        if in_left_pocket or in_right_pocket:
            # Inside the pocket, clamp vertically to the pocket opening height
            pocket_top = goal_top + radius
            pocket_bottom = goal_bottom - radius

            if self.y < pocket_top:
                self.y = pocket_top
                self.vy = 0.0
            elif self.y > pocket_bottom:
                self.y = pocket_bottom
                self.vy = 0.0
        else:
            if self.y < top_bound:
                self.y = top_bound
                self.vy = 0.0
            elif self.y > bottom_bound:
                self.y = bottom_bound
                self.vy = 0.0

    def get_rotated_points(self) -> list[tuple[float, float]]:
        """
        Build a rotated polygon that represents the car.
        """
        local_points = [
            (-self.width / 2, -self.height / 2),
            (self.width / 2, -self.height / 2),
            (self.width / 2, self.height / 2),
            (-self.width / 2, self.height / 2),
        ]

        radians = math.radians(self.angle)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)

        rotated_points = []
        for px, py in local_points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated_points.append((self.x + rx, self.y + ry))

        return rotated_points

    def get_nose_points(self) -> list[tuple[float, float]]:
        """
        Build a small triangle on the front of the car so the player can quickly
        tell which direction the car is facing.
        """
        local_points = [
            (0, -self.height / 2 + 4),
            (-self.width / 4, -self.height / 6),
            (self.width / 4, -self.height / 6),
        ]

        radians = math.radians(self.angle)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)

        rotated_points = []
        for px, py in local_points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            rotated_points.append((self.x + rx, self.y + ry))

        return rotated_points

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the car body and front-direction marker.
        """
        body_points = self.get_rotated_points()
        nose_points = self.get_nose_points()

        pygame.draw.polygon(surface, self.body_color, body_points)
        pygame.draw.polygon(surface, self.nose_color, nose_points)
        pygame.draw.polygon(surface, (20, 20, 20), body_points, width=2)