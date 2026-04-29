"""
ui/hud.py

HUD = heads-up display.

This HUD displays:
- score
- timer
- countdown
- kickoff status
- end-of-match overlay
- side labels for player and AI
- player boost meter
"""

from __future__ import annotations

import pygame
import config
from utils import draw_centered_text, draw_text


class HUD:
    """
    Handles drawing the game's on-screen UI.
    """

    def __init__(self) -> None:
        self.main_font = pygame.font.SysFont(None, config.HUD_FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, config.SMALL_FONT_SIZE)
        self.large_font = pygame.font.SysFont(None, config.LARGE_FONT_SIZE)
        self.result_font = pygame.font.SysFont(None, config.RESULT_FONT_SIZE)
        self.countdown_font = pygame.font.SysFont(None, config.COUNTDOWN_FONT_SIZE)

    def draw_boost_meter(self, surface: pygame.Surface, boost_amount: float) -> None:
        """
        Draw the player's boost meter in the lower-left corner.
        """
        bar_x = 20
        bar_y = config.SCREEN_HEIGHT - 48
        bar_width = 220
        bar_height = 20

        fill_ratio = max(0.0, min(1.0, boost_amount / config.BOOST_MAX))
        fill_width = int(bar_width * fill_ratio)

        pygame.draw.rect(surface, config.BOOST_BAR_BG, (bar_x, bar_y, bar_width, bar_height), border_radius=6)
        pygame.draw.rect(surface, config.BOOST_BAR_FILL, (bar_x, bar_y, fill_width, bar_height), border_radius=6)
        pygame.draw.rect(surface, config.BOOST_BAR_BORDER, (bar_x, bar_y, bar_width, bar_height), width=2, border_radius=6)

        draw_text(
            surface,
            f"Boost: {int(boost_amount)}",
            self.small_font,
            config.HUD_TEXT_COLOR,
            bar_x,
            bar_y - 24,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

    def draw(
        self,
        surface: pygame.Surface,
        left_score: int,
        right_score: int,
        time_text: str,
        player_boost: float,
        message: str = "",
        match_over: bool = False,
        countdown_text: str = "",
        waiting_for_kickoff_touch: bool = False,
    ) -> None:
        """
        Draw the current HUD state.
        """
        # Team labels
        draw_text(
            surface,
            "PLAYER",
            self.small_font,
            config.GOAL_COLOR_LEFT,
            config.SCREEN_WIDTH // 2 - 150,
            20,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        draw_text(
            surface,
            "AI",
            self.small_font,
            config.GOAL_COLOR_RIGHT,
            config.SCREEN_WIDTH // 2 + 90,
            20,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        # Score
        draw_text(
            surface,
            f"{left_score}",
            self.large_font,
            config.GOAL_COLOR_LEFT,
            config.SCREEN_WIDTH // 2 - 80,
            18,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        draw_text(
            surface,
            "-",
            self.large_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2 - 10,
            18,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        draw_text(
            surface,
            f"{right_score}",
            self.large_font,
            config.GOAL_COLOR_RIGHT,
            config.SCREEN_WIDTH // 2 + 30,
            18,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        # Timer
        draw_text(
            surface,
            f"Time: {time_text}",
            self.main_font,
            config.HUD_TEXT_COLOR,
            20,
            20,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        # Controls reminder
        draw_text(
            surface,
            "ESC Pause   R Restart   W/S Drive   A/D Turn   Shift/Space Boost",
            self.small_font,
            config.HUD_TEXT_COLOR,
            20,
            56,
            shadow=True,
            shadow_color=config.HUD_SHADOW_COLOR,
        )

        self.draw_boost_meter(surface, player_boost)

        if countdown_text and not match_over:
            draw_centered_text(
                surface,
                countdown_text,
                self.countdown_font,
                config.HUD_TEXT_COLOR,
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 - 20,
            )

        if waiting_for_kickoff_touch and not countdown_text and not match_over:
            draw_centered_text(
                surface,
                "Clock starts on first touch",
                self.main_font,
                config.HUD_TEXT_COLOR,
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 + 45,
            )

        if message and not match_over and not countdown_text:
            draw_centered_text(
                surface,
                message,
                self.large_font,
                config.HUD_TEXT_COLOR,
                config.SCREEN_WIDTH // 2,
                100,
            )

        if match_over:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(config.OVERLAY_COLOR)
            surface.blit(overlay, (0, 0))

            draw_centered_text(
                surface,
                message,
                self.result_font,
                config.HUD_TEXT_COLOR,
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 - 40,
            )

            draw_centered_text(
                surface,
                "Press R to restart or M for main menu",
                self.main_font,
                config.HUD_TEXT_COLOR,
                config.SCREEN_WIDTH // 2,
                config.SCREEN_HEIGHT // 2 + 34,
            )