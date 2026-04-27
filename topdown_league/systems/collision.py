"""
systems/collision.py

Collision handling for the project.

This file is responsible for:
- ball vs wall collision, with recessed goal pockets
- car vs ball collision
- car vs car collision
"""

from __future__ import annotations

import math

import config
from entities.ball import Ball
from entities.car import Car


def handle_ball_wall_collision(ball: Ball) -> None:
    """
    Bounce the ball off the solid parts of the arena, including the back walls
    of the recessed goals.
    """
    goal_top = (config.SCREEN_HEIGHT - config.GOAL_HEIGHT) // 2
    goal_bottom = goal_top + config.GOAL_HEIGHT

    inside_goal_y = goal_top <= ball.y <= goal_bottom
    inside_left_pocket = ball.x < config.FIELD_MARGIN
    inside_right_pocket = ball.x > config.SCREEN_WIDTH - config.FIELD_MARGIN

    main_left = config.FIELD_MARGIN + ball.radius
    main_right = config.SCREEN_WIDTH - config.FIELD_MARGIN - ball.radius

    left_goal_back = config.FIELD_MARGIN - config.GOAL_DEPTH + ball.radius
    right_goal_back = config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH - ball.radius

    if ball.x < main_left and not inside_goal_y:
        ball.x = main_left
        ball.vx = abs(ball.vx) * config.BALL_WALL_BOUNCE
    elif ball.x > main_right and not inside_goal_y:
        ball.x = main_right
        ball.vx = -abs(ball.vx) * config.BALL_WALL_BOUNCE

    if inside_goal_y:
        if ball.x < left_goal_back:
            ball.x = left_goal_back
            ball.vx = abs(ball.vx) * config.BALL_WALL_BOUNCE
        elif ball.x > right_goal_back:
            ball.x = right_goal_back
            ball.vx = -abs(ball.vx) * config.BALL_WALL_BOUNCE

    if not inside_left_pocket and not inside_right_pocket:
        min_y = config.FIELD_MARGIN + ball.radius
        max_y = config.SCREEN_HEIGHT - config.FIELD_MARGIN - ball.radius
    else:
        min_y = goal_top + ball.radius
        max_y = goal_bottom - ball.radius

    if ball.y < min_y:
        ball.y = min_y
        ball.vy = abs(ball.vy) * config.BALL_WALL_BOUNCE
    elif ball.y > max_y:
        ball.y = max_y
        ball.vy = -abs(ball.vy) * config.BALL_WALL_BOUNCE


def handle_car_ball_collision(car: Car, ball: Ball) -> bool:
    """
    Resolve collision between a car and the ball.

    Returns True if the car touched the ball this frame.
    """
    dx = ball.x - car.x
    dy = ball.y - car.y
    distance = math.hypot(dx, dy)

    minimum_distance = car.collision_radius + ball.radius

    if distance == 0:
        dx = 1.0
        dy = 0.0
        distance = 1.0

    if distance < minimum_distance:
        nx = dx / distance
        ny = dy / distance

        overlap = minimum_distance - distance + config.COLLISION_SEPARATION_BUFFER
        ball.x += nx * overlap
        ball.y += ny * overlap

        car_speed_along_normal = car.vx * nx + car.vy * ny
        impulse = max(1.2, car_speed_along_normal) * config.CAR_BALL_HIT_STRENGTH

        ball.vx += nx * impulse + car.vx * 0.35
        ball.vy += ny * impulse + car.vy * 0.35
        return True

    return False


def handle_car_car_collision(car_a: Car, car_b: Car) -> None:
    """
    Resolve collision between two cars using simple circle-style separation.

    This is intentionally lightweight and arcade-friendly rather than a full
    rigid-body simulation.
    """
    dx = car_b.x - car_a.x
    dy = car_b.y - car_a.y
    distance = math.hypot(dx, dy)

    minimum_distance = car_a.collision_radius + car_b.collision_radius

    if distance == 0:
        dx = 1.0
        dy = 0.0
        distance = 1.0

    if distance < minimum_distance:
        nx = dx / distance
        ny = dy / distance
        overlap = minimum_distance - distance + config.COLLISION_SEPARATION_BUFFER

        # Push both cars apart
        separation_x = nx * (overlap / 2)
        separation_y = ny * (overlap / 2)

        car_a.x -= separation_x
        car_a.y -= separation_y
        car_b.x += separation_x
        car_b.y += separation_y

        # Simple velocity response
        relative_vx = car_b.vx - car_a.vx
        relative_vy = car_b.vy - car_a.vy
        relative_speed_along_normal = relative_vx * nx + relative_vy * ny

        if relative_speed_along_normal < 0:
            impulse = -relative_speed_along_normal * 0.55

            car_a.vx -= nx * impulse
            car_a.vy -= ny * impulse
            car_b.vx += nx * impulse
            car_b.vy += ny * impulse

        # Re-clamp after separation
        car_a.keep_in_bounds()
        car_b.keep_in_bounds()