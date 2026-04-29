"""
game.py

Main game controller for the presentation/polish phase.

Responsibilities:
- create the window and clock
- manage state flow between menu / playing / paused
- handle quit and restart events
- update player and AI cars
- update the ball
- resolve collisions
- detect goals
- track score and timer
- reset positions after goals
- run kickoff countdown
- pause game timer until first touch after kickoff
- show result overlays
- trigger simple procedural sound effects
"""

from __future__ import annotations

import pygame

import config
from entities.ai_car import AICar
from entities.ball import Ball
from entities.player_car import PlayerCar
from systems.ai_controller import AIController
from systems.audio_manager import AudioManager
from systems.collision import (
    handle_ball_wall_collision,
    handle_car_ball_collision,
    handle_car_car_collision,
)
from systems.input_handler import get_player1_actions
from systems.scoring import ScoreSystem
from ui.hud import HUD
from ui.menu import MenuUI


class Game:
    """
    Main game object that manages the runtime loop and screen states.
    """

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "menu"   # menu, playing, paused

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
        self.audio = AudioManager()
        self.score_system = ScoreSystem()
        self.hud = HUD()
        self.menu_ui = MenuUI()

        # Used so countdown beeps fire once per visible number
        self.last_countdown_text = ""

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
        self.audio.stop_all_loops()

    def start_new_match(self) -> None:
        """
        Start a fresh match from the menu.
        """
        self.score_system.reset_match()
        self.reset_positions()
        self.last_countdown_text = ""
        self.state = "playing"

    def return_to_menu(self) -> None:
        """
        Return to the title menu.
        """
        self.audio.stop_all_loops()
        self.state = "menu"

    def reset_match(self) -> None:
        """
        Reset the current match state and kickoff setup.
        """
        self.score_system.reset_match()
        self.reset_positions()
        self.last_countdown_text = ""
        self.state = "playing"

    def handle_events(self) -> None:
        """
        Handle pygame events based on the current screen state.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.start_new_match()

                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.audio.stop_all_loops()
                        self.state = "paused"
                    elif event.key == pygame.K_r:
                        self.reset_match()
                    elif event.key == pygame.K_m and self.score_system.match_over:
                        self.return_to_menu()

                elif self.state == "paused":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                    elif event.key == pygame.K_r:
                        self.reset_match()
                    elif event.key == pygame.K_m:
                        self.return_to_menu()

    def handle_countdown_sounds(self) -> None:
        """
        Play countdown sounds once as the visible text changes.
        """
        countdown_text = self.score_system.get_countdown_text()

        if countdown_text != self.last_countdown_text:
            if countdown_text in {"1", "2", "3"}:
                self.audio.play_countdown_beep()
            elif self.last_countdown_text in {"1", "2", "3"} and countdown_text == "":
                # Fallback if GO text is too brief or hidden by update timing
                self.audio.play_countdown_go()

            self.last_countdown_text = countdown_text

        # If the scoring system uses "GO!" as message after countdown, play it once.
        if not self.score_system.countdown_active and self.score_system.message == "GO!":
            if self.last_countdown_text != "GO":
                self.audio.play_countdown_go()
                self.last_countdown_text = "GO"

    def update(self, dt_seconds: float) -> None:
        """
        Update gameplay only while actively playing.
        """
        self.audio.update()

        if self.state != "playing":
            self.audio.stop_all_loops()
            return

        self.score_system.update_timer(dt_seconds)

        if self.score_system.match_over:
            self.audio.stop_all_loops()
            return

        if self.score_system.countdown_active:
            self.audio.stop_all_loops()
            self.score_system.update_kickoff_countdown(dt_seconds)
            self.handle_countdown_sounds()
            return

        keys = pygame.key.get_pressed()
        player_actions = get_player1_actions(keys)
        ai_actions = self.ai_controller.get_actions(self.ai_car, self.ball)

        # Engine and boost sound should mostly reflect player input/state
        player_engine_active = player_actions["accelerate"] or player_actions["reverse"]
        player_boost_active = (
            player_actions["boost"]
            and player_actions["accelerate"]
            and self.player_car.boost_amount >= config.BOOST_MIN_TO_ACTIVATE
        )

        self.audio.set_engine_active(player_engine_active)
        self.audio.set_boost_active(player_boost_active)

        self.player_car.update_from_actions(player_actions)
        self.ai_car.update_from_actions(ai_actions)
        self.ball.update()

        pre_ball_vx = self.ball.vx
        pre_ball_vy = self.ball.vy
        pre_player_vx = self.player_car.vx
        pre_player_vy = self.player_car.vy
        pre_ai_vx = self.ai_car.vx
        pre_ai_vy = self.ai_car.vy

        handle_ball_wall_collision(self.ball)

        player_touched = handle_car_ball_collision(self.player_car, self.ball)
        ai_touched = handle_car_ball_collision(self.ai_car, self.ball)

        handle_car_car_collision(self.player_car, self.ai_car)

        # Impact sound hooks
        if player_touched or ai_touched:
            ball_speed_delta = abs(self.ball.vx - pre_ball_vx) + abs(self.ball.vy - pre_ball_vy)
            self.audio.play_impact(ball_speed_delta)

        car_speed_delta = (
            abs(self.player_car.vx - pre_player_vx)
            + abs(self.player_car.vy - pre_player_vy)
            + abs(self.ai_car.vx - pre_ai_vx)
            + abs(self.ai_car.vy - pre_ai_vy)
        )
        if car_speed_delta > 1.4:
            self.audio.play_impact(car_speed_delta * 0.6)

        if player_touched or ai_touched:
            self.score_system.notify_ball_touched_after_kickoff()

        old_left = self.score_system.left_score
        old_right = self.score_system.right_score

        goal_scored = self.score_system.check_goal(self.ball)
        if goal_scored is not None:
            if (
                self.score_system.left_score != old_left
                or self.score_system.right_score != old_right
            ):
                self.audio.play_goal()

            self.reset_positions()
            self.last_countdown_text = ""

    def draw_background_and_field(self) -> None:
        """
        Draw the arena with slightly nicer presentation.
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

        inner_rect = field_rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, (45, 125, 82), inner_rect, width=2, border_radius=10)

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

        pygame.draw.circle(
            self.screen,
            config.FIELD_LINE_COLOR,
            (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
            6,
        )

    def draw_game_scene(self) -> None:
        """
        Draw the active match scene.
        """
        self.draw_background_and_field()
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

    def draw(self) -> None:
        """
        Draw one full frame based on the current state.
        """
        if self.state == "menu":
            self.draw_background_and_field()
            self.menu_ui.draw_main_menu(self.screen)

        elif self.state == "playing":
            self.draw_game_scene()

        elif self.state == "paused":
            self.draw_game_scene()
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            self.menu_ui.draw_pause_menu(self.screen)

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