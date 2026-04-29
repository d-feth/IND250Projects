"""
systems/ai_controller.py

Rule-based AI controller for the opponent car.

This AI is intentionally simple and understandable.

Main goals:
- Do not cheat
- Use the same movement system as the player
- Be believable enough to play against
- Stay readable for a school project

This version adds specific wall and corner behavior so the AI does not
get stuck turning in loops when the ball is trapped near boundaries.
"""

from __future__ import annotations

import math

import config
from entities.ai_car import AICar
from entities.ball import Ball


class AIController:
    """
    Builds action dictionaries for the AI car.
    """

    def __init__(self) -> None:
        # Small recovery state to help the AI stop spinning uselessly near walls
        self.escape_turn_timer = 0
        self.escape_turn_direction = 1

    def get_actions(self, ai_car: AICar, ball: Ball) -> dict[str, bool]:
        """
        Return a dictionary of movement actions for the AI car.
        """
        if self.should_enter_escape_mode(ai_car):
            if self.escape_turn_timer == 0:
                self.escape_turn_timer = config.AI_ESCAPE_TURN_FRAMES
                self.escape_turn_direction = self.choose_escape_turn_direction(ai_car, ball)

        if self.escape_turn_timer > 0:
            self.escape_turn_timer -= 1
            return {
                "accelerate": True,
                "reverse": False,
                "turn_left": self.escape_turn_direction < 0,
                "turn_right": self.escape_turn_direction > 0,
                "boost": False,
            }

        target_x, target_y = self.choose_target(ai_car, ball)
        return self.drive_toward_target(ai_car, target_x, target_y)

    def choose_target(self, ai_car: AICar, ball: Ball) -> tuple[float, float]:
        """
        Decide where the AI wants to go.

        Priority:
        1. Corner handling
        2. Wall handling
        3. Defense
        4. Normal attacking approach
        """
        if self.ball_in_corner(ball):
            return self.get_corner_recovery_target(ball)

        if self.ball_near_wall(ball):
            return self.get_wall_play_target(ball)

        if ball.x > config.SCREEN_WIDTH * 0.62:
            return self.get_defensive_target(ai_car, ball)

        return self.get_attack_target(ai_car, ball)

    def ball_near_wall(self, ball: Ball) -> bool:
        """
        Return True if the ball is close to one wall but not deeply in a corner.
        """
        wall_buffer = 80

        near_left = ball.x < config.FIELD_MARGIN + wall_buffer
        near_right = ball.x > config.SCREEN_WIDTH - config.FIELD_MARGIN - wall_buffer
        near_top = ball.y < config.FIELD_MARGIN + wall_buffer
        near_bottom = ball.y > config.SCREEN_HEIGHT - config.FIELD_MARGIN - wall_buffer

        count = sum([near_left, near_right, near_top, near_bottom])

        # One nearby wall = wall case
        return count == 1

    def ball_in_corner(self, ball: Ball) -> bool:
        """
        Return True if the ball is near a top/bottom and left/right wall together.
        """
        corner_buffer = 95

        near_left = ball.x < config.FIELD_MARGIN + corner_buffer
        near_right = ball.x > config.SCREEN_WIDTH - config.FIELD_MARGIN - corner_buffer
        near_top = ball.y < config.FIELD_MARGIN + corner_buffer
        near_bottom = ball.y > config.SCREEN_HEIGHT - config.FIELD_MARGIN - corner_buffer

        return (near_left or near_right) and (near_top or near_bottom)

    def get_corner_recovery_target(self, ball: Ball) -> tuple[float, float]:
        """
        When the ball is in a corner, do not drive directly at it.
        Instead, target a point just outside the corner so the AI can approach
        from a better angle and avoid spinning in place.
        """
        offset = 110

        target_x = ball.x
        target_y = ball.y

        if ball.x < config.SCREEN_WIDTH / 2:
            target_x += offset
        else:
            target_x -= offset

        if ball.y < config.SCREEN_HEIGHT / 2:
            target_y += offset
        else:
            target_y -= offset

        return target_x, target_y

    def get_wall_play_target(self, ball: Ball) -> tuple[float, float]:
        """
        When the ball is near a wall, target a point slightly away from the wall
        so the AI approaches from an angle instead of ramming directly into it.
        """
        offset = 85
        target_x = ball.x
        target_y = ball.y

        if ball.x < config.FIELD_MARGIN + 90:
            target_x += offset
        elif ball.x > config.SCREEN_WIDTH - config.FIELD_MARGIN - 90:
            target_x -= offset

        if ball.y < config.FIELD_MARGIN + 90:
            target_y += offset
        elif ball.y > config.SCREEN_HEIGHT - config.FIELD_MARGIN - 90:
            target_y -= offset

        return target_x, target_y

    def get_defensive_target(self, ai_car: AICar, ball: Ball) -> tuple[float, float]:
        """
        If the ball is threatening the AI's side, fall back into a defensive lane.
        """
        defend_y = max(
            config.FIELD_MARGIN + ai_car.collision_radius,
            min(config.SCREEN_HEIGHT - config.FIELD_MARGIN - ai_car.collision_radius, ball.y),
        )
        return config.AI_DEFEND_X, defend_y

    def get_attack_target(self, ai_car: AICar, ball: Ball) -> tuple[float, float]:
        """
        Default attack setup:
        approach from the AI side of the ball so the AI tends to hit leftward
        toward the player's goal.
        """
        offset_x = 95
        offset_y = (ball.y - ai_car.y) * 0.16

        target_x = ball.x + offset_x
        target_y = ball.y + offset_y

        return target_x, target_y

    def should_enter_escape_mode(self, ai_car: AICar) -> bool:
        """
        Detect whether the AI is in a bad wall-adjacent situation where it tends
        to get stuck turning in loops.
        """
        near_left = ai_car.x < config.FIELD_MARGIN + config.AI_WALL_X_BUFFER
        near_right = ai_car.x > config.SCREEN_WIDTH - config.FIELD_MARGIN - config.AI_WALL_X_BUFFER
        near_top = ai_car.y < config.FIELD_MARGIN + config.AI_WALL_Y_BUFFER
        near_bottom = ai_car.y > config.SCREEN_HEIGHT - config.FIELD_MARGIN - config.AI_WALL_Y_BUFFER

        speed = math.hypot(ai_car.vx, ai_car.vy)

        return (near_left or near_right or near_top or near_bottom) and speed < 1.2

    def choose_escape_turn_direction(self, ai_car: AICar, ball: Ball) -> int:
        """
        Pick a temporary turn direction that tends to point the AI back toward
        more open field space.
        """
        if ball.y < ai_car.y:
            return -1
        return 1

    def drive_toward_target(self, ai_car: AICar, target_x: float, target_y: float) -> dict[str, bool]:
        """
        Convert a target point into car control actions.
        """
        dx = target_x - ai_car.x
        dy = target_y - ai_car.y

        target_angle = self.world_vector_to_car_angle(dx, dy)
        angle_diff = self.normalize_angle(target_angle - ai_car.angle)
        distance = math.hypot(dx, dy)

        turn_left = angle_diff < -config.AI_STEER_DEADZONE
        turn_right = angle_diff > config.AI_STEER_DEADZONE

        should_reverse = abs(angle_diff) > config.AI_REVERSE_ANGLE_THRESHOLD and distance < 110
        accelerate = not should_reverse
        reverse = should_reverse

        boost = (
            accelerate
            and abs(angle_diff) < config.AI_BOOST_ANGLE_THRESHOLD
            and distance > config.AI_BOOST_DISTANCE_THRESHOLD
            and ai_car.boost_amount > 12
        )

        return {
            "accelerate": accelerate,
            "reverse": reverse,
            "turn_left": turn_left,
            "turn_right": turn_right,
            "boost": boost,
        }

    @staticmethod
    def world_vector_to_car_angle(dx: float, dy: float) -> float:
        """
        Convert a world-space direction vector into the angle convention used
        by the car drawing/movement system.
        """
        return math.degrees(math.atan2(dy, dx)) + 90

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """
        Normalize an angle into the range [-180, 180].
        """
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle