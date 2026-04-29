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
- draw the car as a more detailed top-down Octane-inspired shape
- spawn simple boost trail puffs
- expose a collision radius for simple physics interactions
"""

from __future__ import annotations

import math
import pygame

import config
from utils import limit_vector


class Car:
    """
    Base car class with shared movement, boost, trail, and drawing behavior.
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

        self.boost_amount = config.BOOST_MAX

        # Visual boost trail puffs
        self.boost_puffs: list[dict[str, float]] = []
        self.boost_spawn_timer = 0

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
        self.boost_puffs.clear()
        self.boost_spawn_timer = 0

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
        self.update_boost_puffs(boost_active)

    def keep_in_bounds(self) -> None:
        """
        Keep the car inside the arena, including recessed goal pockets.
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

        in_left_pocket = self.x < config.FIELD_MARGIN and goal_top <= self.y <= goal_bottom
        in_right_pocket = self.x > config.SCREEN_WIDTH - config.FIELD_MARGIN and goal_top <= self.y <= goal_bottom

        if in_left_pocket:
            if self.x < left_pocket_back:
                self.x = left_pocket_back
                self.vx = 0.0

        elif in_right_pocket:
            if self.x > right_pocket_back:
                self.x = right_pocket_back
                self.vx = 0.0

        else:
            goal_mouth_y = goal_top <= self.y <= goal_bottom

            if self.x < main_left and not goal_mouth_y:
                self.x = main_left
                self.vx = 0.0
            elif self.x > main_right and not goal_mouth_y:
                self.x = main_right
                self.vx = 0.0

        if in_left_pocket or in_right_pocket:
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

    def update_boost_puffs(self, boost_active: bool) -> None:
        """
        Update the boost trail puffs.

        These puffs are intentionally simple:
        - they spawn near the rear of the car
        - they do not move after spawning
        - they fade from orange to gray
        - they slowly grow and disappear
        """
        if boost_active:
            self.boost_spawn_timer += 1
            if self.boost_spawn_timer >= config.BOOST_PUFF_SPAWN_INTERVAL:
                self.boost_spawn_timer = 0
                self.spawn_boost_puffs()
        else:
            self.boost_spawn_timer = 0

        for puff in self.boost_puffs[:]:
            puff["life"] -= 1
            puff["radius"] += config.BOOST_PUFF_GROWTH

            if puff["life"] <= 0:
                self.boost_puffs.remove(puff)

    def spawn_boost_puffs(self) -> None:
        """
        Spawn a pair of exhaust puffs from the rear of the car.
        """
        rear_left = self.local_to_world(-self.width * 0.18, self.height * 0.48)
        rear_right = self.local_to_world(self.width * 0.18, self.height * 0.48)

        for px, py in (rear_left, rear_right):
            self.boost_puffs.append(
                {
                    "x": px,
                    "y": py,
                    "radius": float(config.BOOST_PUFF_RADIUS),
                    "life": float(config.BOOST_PUFF_LIFE),
                    "max_life": float(config.BOOST_PUFF_LIFE),
                }
            )

    def local_to_world(self, local_x: float, local_y: float) -> tuple[float, float]:
        """
        Convert a point from the car's local space into world space.
        """
        radians = math.radians(self.angle)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)

        world_x = self.x + (local_x * cos_a - local_y * sin_a)
        world_y = self.y + (local_x * sin_a + local_y * cos_a)
        return world_x, world_y

    def transform_points(self, local_points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """
        Transform a list of local-space points into world-space points.
        """
        return [self.local_to_world(px, py) for px, py in local_points]

    def draw_boost_puffs(self, surface: pygame.Surface) -> None:
        """
        Draw the current boost puffs.
        """
        for puff in self.boost_puffs:
            life_ratio = puff["life"] / puff["max_life"]

            r1, g1, b1 = config.BOOST_START_COLOR
            r2, g2, b2 = config.BOOST_END_COLOR

            color = (
                int(r2 + (r1 - r2) * life_ratio),
                int(g2 + (g1 - g2) * life_ratio),
                int(b2 + (b1 - b2) * life_ratio),
            )

            alpha = int(255 * life_ratio)
            radius = int(puff["radius"])

            puff_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                puff_surface,
                (*color, alpha),
                (radius + 2, radius + 2),
                radius,
            )

            surface.blit(
                puff_surface,
                (int(puff["x"] - radius - 2), int(puff["y"] - radius - 2)),
            )

    def draw_wheels(self, surface: pygame.Surface) -> None:
        """
        Draw four simple wheel hints near the corners of the car.
        """
        wheel_positions = [
            (-self.width * 0.42, -self.height * 0.22),
            (self.width * 0.42, -self.height * 0.22),
            (-self.width * 0.42, self.height * 0.22),
            (self.width * 0.42, self.height * 0.22),
        ]

        for local_x, local_y in wheel_positions:
            wx, wy = self.local_to_world(local_x, local_y)
            pygame.draw.circle(surface, config.CAR_WHEEL_COLOR, (int(wx), int(wy)), 6)
            pygame.draw.circle(surface, config.CAR_WHEEL_HUB_COLOR, (int(wx), int(wy)), 2)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the car with a more detailed top-down look.

        Layout:
        - body shell
        - stripes on hood and rear deck only
        - front windshield
        - two side windows
        - nose marker
        """
        self.draw_boost_puffs(surface)
        self.draw_wheels(surface)

        # Outer body shape
        body_points = self.transform_points(
            [
                (0, -self.height * 0.52),
                (self.width * 0.30, -self.height * 0.44),
                (self.width * 0.47, -self.height * 0.16),
                (self.width * 0.47, self.height * 0.22),
                (self.width * 0.30, self.height * 0.48),
                (-self.width * 0.30, self.height * 0.48),
                (-self.width * 0.47, self.height * 0.22),
                (-self.width * 0.47, -self.height * 0.16),
                (-self.width * 0.30, -self.height * 0.44),
            ]
        )

        pygame.draw.polygon(surface, self.body_color, body_points)
        pygame.draw.polygon(surface, config.CAR_OUTLINE_COLOR, body_points, width=2)

        # Hood stripes (front section only)
        left_hood_stripe = self.transform_points(
            [
                (-self.width * 0.10, -self.height * 0.42),
                (-self.width * 0.03, -self.height * 0.42),
                (-self.width * 0.03, -self.height * 0.18),
                (-self.width * 0.10, -self.height * 0.18),
            ]
        )
        right_hood_stripe = self.transform_points(
            [
                (self.width * 0.03, -self.height * 0.42),
                (self.width * 0.10, -self.height * 0.42),
                (self.width * 0.10, -self.height * 0.18),
                (self.width * 0.03, -self.height * 0.18),
            ]
        )

        # Rear deck stripes (rear section only)
        left_rear_stripe = self.transform_points(
            [
                (-self.width * 0.10, self.height * 0.14),
                (-self.width * 0.03, self.height * 0.14),
                (-self.width * 0.03, self.height * 0.40),
                (-self.width * 0.10, self.height * 0.40),
            ]
        )
        right_rear_stripe = self.transform_points(
            [
                (self.width * 0.03, self.height * 0.14),
                (self.width * 0.10, self.height * 0.14),
                (self.width * 0.10, self.height * 0.40),
                (self.width * 0.03, self.height * 0.40),
            ]
        )

        for stripe in (left_hood_stripe, right_hood_stripe, left_rear_stripe, right_rear_stripe):
            pygame.draw.polygon(surface, config.CAR_STRIPE_COLOR, stripe)

        # Front windshield
        windshield_points = self.transform_points(
            [
                (-self.width * 0.22, -self.height * 0.16),
                (self.width * 0.22, -self.height * 0.16),
                (self.width * 0.14, -self.height * 0.02),
                (-self.width * 0.14, -self.height * 0.02),
            ]
        )
        pygame.draw.polygon(surface, config.CAR_WINDOW_COLOR, windshield_points)
        pygame.draw.polygon(surface, config.CAR_OUTLINE_COLOR, windshield_points, width=1)

        # Side windows
        left_window_points = self.transform_points(
            [
                (-self.width * 0.28, -self.height * 0.02),
                (-self.width * 0.10, -self.height * 0.02),
                (-self.width * 0.10, self.height * 0.18),
                (-self.width * 0.24, self.height * 0.12),
            ]
        )
        right_window_points = self.transform_points(
            [
                (self.width * 0.10, -self.height * 0.02),
                (self.width * 0.28, -self.height * 0.02),
                (self.width * 0.24, self.height * 0.12),
                (self.width * 0.10, self.height * 0.18),
            ]
        )

        pygame.draw.polygon(surface, config.CAR_WINDOW_COLOR, left_window_points)
        pygame.draw.polygon(surface, config.CAR_WINDOW_COLOR, right_window_points)
        pygame.draw.polygon(surface, config.CAR_OUTLINE_COLOR, left_window_points, width=1)
        pygame.draw.polygon(surface, config.CAR_OUTLINE_COLOR, right_window_points, width=1)

        # Small hood nose marker
        nose_points = self.transform_points(
            [
                (0, -self.height * 0.50),
                (-self.width * 0.10, -self.height * 0.36),
                (self.width * 0.10, -self.height * 0.36),
            ]
        )
        pygame.draw.polygon(surface, self.nose_color, nose_points)