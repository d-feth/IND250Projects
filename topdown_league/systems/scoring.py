"""
systems/scoring.py

This file handles match rules related to:
- goal detection
- score tracking
- kickoff countdowns
- paused clock until first touch
- winner calculation

Keeping this separate from rendering and collision helps the project stay
organized as it grows.
"""

from __future__ import annotations

import math
import config
from entities.ball import Ball


class ScoreSystem:
    """
    Manages score, timer, kickoff flow, and match result state.
    """

    def __init__(self) -> None:
        self.left_score = 0
        self.right_score = 0

        self.time_remaining = float(config.MATCH_TIME_SECONDS)
        self.match_over = False

        # Kickoff state
        self.countdown_active = True
        self.countdown_remaining = float(config.KICKOFF_COUNTDOWN_SECONDS)

        # Timer stays paused until the ball is touched after kickoff release
        self.waiting_for_kickoff_touch = True

        self.message = ""
        self.goal_message = ""

    def reset_match(self) -> None:
        """
        Reset the full match state to starting values.
        """
        self.left_score = 0
        self.right_score = 0
        self.time_remaining = float(config.MATCH_TIME_SECONDS)
        self.match_over = False

        self.start_kickoff_countdown()
        self.goal_message = ""

    def start_kickoff_countdown(self) -> None:
        """
        Start a frozen countdown before kickoff begins.
        """
        self.countdown_active = True
        self.countdown_remaining = float(config.KICKOFF_COUNTDOWN_SECONDS)
        self.waiting_for_kickoff_touch = True
        self.message = ""
        self.goal_message = ""

    def start_post_goal_kickoff(self, scorer_text: str) -> None:
        """
        Begin the post-goal reset flow.
        """
        self.countdown_active = True
        self.countdown_remaining = float(config.KICKOFF_COUNTDOWN_SECONDS)
        self.waiting_for_kickoff_touch = True
        self.goal_message = scorer_text
        self.message = scorer_text

    def update_timer(self, dt_seconds: float) -> None:
        """
        Reduce the remaining match time only when gameplay clock is active.
        """
        if self.match_over:
            return

        if self.countdown_active:
            return

        if self.waiting_for_kickoff_touch:
            return

        self.time_remaining -= dt_seconds

        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.match_over = True
            self.message = self.get_result_text()

    def update_kickoff_countdown(self, dt_seconds: float) -> None:
        """
        Update the countdown before a kickoff becomes live.
        """
        if not self.countdown_active or self.match_over:
            return

        self.countdown_remaining -= dt_seconds

        if self.countdown_remaining <= 0:
            self.countdown_remaining = 0
            self.countdown_active = False
            self.goal_message = ""
            self.message = "GO!"

    def notify_ball_touched_after_kickoff(self) -> None:
        """
        Once the ball is touched after kickoff, start the match clock/resume it.
        """
        if self.match_over:
            return

        if not self.countdown_active and self.waiting_for_kickoff_touch:
            self.waiting_for_kickoff_touch = False
            self.message = ""

    def get_goal_bounds(self) -> tuple[int, int]:
        """
        Return the top and bottom y-values of the goal opening.
        """
        goal_top = (config.SCREEN_HEIGHT - config.GOAL_HEIGHT) // 2
        goal_bottom = goal_top + config.GOAL_HEIGHT
        return goal_top, goal_bottom

    def check_goal(self, ball: Ball) -> str | None:
        """
        Check whether the ball is fully inside a goal pocket.

        This only counts a goal when the ENTIRE ball is past the field opening,
        which creates more real save opportunities near the line.

        Returns:
        - "left" if ball is fully inside left goal pocket
        - "right" if ball is fully inside right goal pocket
        - None otherwise
        """
        if self.match_over or self.countdown_active:
            return None

        goal_top, goal_bottom = self.get_goal_bounds()
        inside_goal_y = goal_top <= ball.y <= goal_bottom

        if not inside_goal_y:
            return None

        # Entire ball must be inside left pocket
        if ball.x + ball.radius <= config.FIELD_MARGIN:
            self.right_score += 1
            self.start_post_goal_kickoff("GOAL! Right side scores!")
            return "left"

        # Entire ball must be inside right pocket
        if ball.x - ball.radius >= config.SCREEN_WIDTH - config.FIELD_MARGIN:
            self.left_score += 1
            self.start_post_goal_kickoff("GOAL! Left side scores!")
            return "right"

        return None

    def get_result_text(self) -> str:
        """
        Return the final result string based on the current score.
        """
        if self.left_score > self.right_score:
            return "Left Side Wins!"
        if self.right_score > self.left_score:
            return "Right Side Wins!"
        return "Tie Game!"

    def get_time_text(self) -> str:
        """
        Return remaining time in M:SS format.
        """
        total_seconds = max(0, int(self.time_remaining))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_countdown_text(self) -> str:
        """
        Return a human-readable kickoff countdown message.
        """
        if not self.countdown_active:
            return ""

        number = max(1, math.ceil(self.countdown_remaining))
        return str(number)