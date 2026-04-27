"""
game.py

Main game controller for the refined gameplay phase.

Responsibilities:
- create the window and clock
- manage the main loop
- handle quit and restart events
- update player and AI cars
- update the ball
- resolve collisions
- detect goals
- track score and timer
- reset positions after goals
- run kickoff countdown
- pause game timer until first touch after kickoff
- show end-of-match result
"""

from __future__ import annotations

import pygame

import config
from entities.ai_car import AICar
from entities.ball import Ball
from entities.player_car import PlayerCar
from systems.ai_controller import AIController
from systems.collision import (
    handle_ball_wall_collision,
    handle_car_ball_collision,
    handle_car_car_collision,
)
from systems.input_handler import get_player1_actions
from systems.scoring import ScoreSystem
from ui.hud import HUD


class Game:
    """
    Main game object that manages the runtime loop.
    """

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.player_car = PlayerCar(
            config.PLAYER_KICKOFF_X,
            config.PLAYER_KICKOFF_Y,
        )

        self.ai_car = AICar(
            config.AI_KICKOFF_X,
            config.AI_KICKOFF_Y,
        )

        self.ball = Ball(config.BALL_START_X, config.BALL_START_Y)

        self.ai_controller = AIController()
        self.score_system = ScoreSystem()
        self.hud = HUD()

        self.reset_positions()

    def reset_positions(self) -> None:
        """
        Reset both cars and the ball to kickoff positions.
        """
        self.player_car.reset(
            config.PLAYER_KICKOFF_X,
            config.PLAYER_KICKOFF_Y,
            config.PLAYER_KICKOFF_ANGLE,
        )

        self.ai_car.reset(
            config.AI_KICKOFF_X,
            config.AI_KICKOFF_Y,
            config.AI_KICKOFF_ANGLE,
        )

        self.ball.reset(config.BALL_START_X, config.BALL_START_Y)

    def reset_match(self) -> None:
        """
        Reset the full match state and kickoff setup.
        """
        self.score_system.reset_match()
        self.reset_positions()

    def handle_events(self) -> None:
        """
        Handle pygame events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_match()

    def update(self, dt_seconds: float) -> None:
        """
        Update all game logic for one frame.
        """
        self.score_system.update_timer(dt_seconds)

        if self.score_system.match_over:
            return

        if self.score_system.countdown_active:
            self.score_system.update_kickoff_countdown(dt_seconds)
            return

        keys = pygame.key.get_pressed()
        player_actions = get_player1_actions(keys)
        ai_actions = self.ai_controller.get_actions(self.ai_car, self.ball)

        self.player_car.update_from_actions(player_actions)
        self.ai_car.update_from_actions(ai_actions)
        self.ball.update()

        handle_ball_wall_collision(self.ball)

        # Car-ball collisions
        player_touched = handle_car_ball_collision(self.player_car, self.ball)
        ai_touched = handle_car_ball_collision(self.ai_car, self.ball)

        # Car-car collision
        handle_car_car_collision(self.player_car, self.ai_car)

        if player_touched or ai_touched:
            self.score_system.notify_ball_touched_after_kickoff()

        goal_scored = self.score_system.check_goal(self.ball)
        if goal_scored is not None:
            self.reset_positions()

    def draw_field(self) -> None:
        """
        Draw the top-down arena with recessed goals.
        """
        self.screen.fill(config.BACKGROUND_COLOR)

        goal_top = (config.SCREEN_HEIGHT - config.GOAL_HEIGHT) // 2
        goal_bottom = goal_top + config.GOAL_HEIGHT

        field_rect = pygame.Rect(
            config.FIELD_MARGIN,
            config.FIELD_MARGIN,
            config.SCREEN_WIDTH - config.FIELD_MARGIN * 2,
            config.SCREEN_HEIGHT - config.FIELD_MARGIN * 2,
        )
        pygame.draw.rect(self.screen, config.FIELD_COLOR, field_rect)

        left_goal_rect = pygame.Rect(
            config.FIELD_MARGIN - config.GOAL_DEPTH,
            goal_top,
            config.GOAL_DEPTH,
            config.GOAL_HEIGHT,
        )
        right_goal_rect = pygame.Rect(
            config.SCREEN_WIDTH - config.FIELD_MARGIN,
            goal_top,
            config.GOAL_DEPTH,
            config.GOAL_HEIGHT,
        )

        pygame.draw.rect(self.screen, (28, 86, 140), left_goal_rect)
        pygame.draw.rect(self.screen, (145, 78, 78), right_goal_rect)

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN, config.FIELD_MARGIN),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, config.FIELD_MARGIN),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN, config.SCREEN_HEIGHT - config.FIELD_MARGIN),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, config.SCREEN_HEIGHT - config.FIELD_MARGIN),
            width=4,
        )

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN, config.FIELD_MARGIN),
            (config.FIELD_MARGIN, goal_top),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN, goal_bottom),
            (config.FIELD_MARGIN, config.SCREEN_HEIGHT - config.FIELD_MARGIN),
            width=4,
        )

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, config.FIELD_MARGIN),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, goal_top),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, goal_bottom),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, config.SCREEN_HEIGHT - config.FIELD_MARGIN),
            width=4,
        )

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN - config.GOAL_DEPTH, goal_top),
            (config.FIELD_MARGIN - config.GOAL_DEPTH, goal_bottom),
            width=4,
        )

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH, goal_top),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH, goal_bottom),
            width=4,
        )

        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN - config.GOAL_DEPTH, goal_top),
            (config.FIELD_MARGIN, goal_top),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.FIELD_MARGIN - config.GOAL_DEPTH, goal_bottom),
            (config.FIELD_MARGIN, goal_bottom),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, goal_top),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH, goal_top),
            width=4,
        )
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH - config.FIELD_MARGIN, goal_bottom),
            (config.SCREEN_WIDTH - config.FIELD_MARGIN + config.GOAL_DEPTH, goal_bottom),
            width=4,
        )

        center_x = config.SCREEN_WIDTH // 2
        pygame.draw.line(
            self.screen,
            config.FIELD_LINE_COLOR,
            (center_x, config.FIELD_MARGIN),
            (center_x, config.SCREEN_HEIGHT - config.FIELD_MARGIN),
            width=4,
        )

        pygame.draw.circle(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
            config.CENTER_CIRCLE_RADIUS,
            width=4,
        )

    def draw(self) -> None:
        """
        Draw one full frame.
        """
        self.draw_field()
        self.ball.draw(self.screen)
        self.player_car.draw(self.screen)
        self.ai_car.draw(self.screen)

        self.hud.draw(
            self.screen,
            left_score=self.score_system.left_score,
            right_score=self.score_system.right_score,
            time_text=self.score_system.get_time_text(),
            player_boost=self.player_car.boost_amount,
            message=self.score_system.message,
            match_over=self.score_system.match_over,
            countdown_text=self.score_system.get_countdown_text(),
            waiting_for_kickoff_touch=self.score_system.waiting_for_kickoff_touch,
        )

        pygame.display.flip()

    def run(self) -> None:
        """
        Main loop.
        """
        while self.running:
            dt_seconds = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt_seconds)
            self.draw()