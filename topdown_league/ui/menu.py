"""
ui/menu.py

Menu system for the top-down car soccer project.

This file handles:
- main menu screen
- pause screen
- drawing shared menu-style buttons and headings

We are keeping the menu system simple and keyboard-driven so it stays stable
and easy to understand for a school final project.
"""

from __future__ import annotations

import pygame
import config
from utils import draw_centered_text


class MenuUI:
    """
    Draws the game's menu-style screens.
    """

    def __init__(self) -> None:
        self.title_font = pygame.font.SysFont(None, 84)
        self.subtitle_font = pygame.font.SysFont(None, 36)
        self.option_font = pygame.font.SysFont(None, 42)
        self.small_font = pygame.font.SysFont(None, 24)

    def draw_panel(self, surface: pygame.Surface, width: int = 760, height: int = 420) -> pygame.Rect:
        """
        Draw a centered translucent panel and return its rectangle.
        """
        panel_x = (config.SCREEN_WIDTH - width) // 2
        panel_y = (config.SCREEN_HEIGHT - height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, width, height)

        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surface.fill((10, 14, 20, 210))
        surface.blit(panel_surface, (panel_x, panel_y))

        pygame.draw.rect(surface, config.FIELD_LINE_COLOR, panel_rect, width=3, border_radius=12)
        return panel_rect

    def draw_main_menu(self, surface: pygame.Surface) -> None:
        """
        Draw the title screen.
        """
        self.draw_panel(surface)

        draw_centered_text(
            surface,
            "Top-Down League",
            self.title_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2,
            185,
        )

        draw_centered_text(
            surface,
            "A 2D top-down car soccer game",
            self.subtitle_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2,
            245,
        )

        draw_centered_text(
            surface,
            "Press ENTER to Start",
            self.option_font,
            config.GOAL_COLOR_LEFT,
            config.SCREEN_WIDTH // 2,
            345,
        )

        draw_centered_text(
            surface,
            "Press ESC during a match to Pause",
            self.option_font,
            config.GOAL_COLOR_RIGHT,
            config.SCREEN_WIDTH // 2,
            395,
        )

        draw_centered_text(
            surface,
            "Controls: W/S to drive, A/D to turn, Shift or Space to boost, R to restart",
            self.small_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2,
            485,
        )

    def draw_pause_menu(self, surface: pygame.Surface) -> None:
        """
        Draw the pause overlay/menu.
        """
        self.draw_panel(surface, width=700, height=340)

        draw_centered_text(
            surface,
            "Paused",
            self.title_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2,
            235,
        )

        draw_centered_text(
            surface,
            "Press ESC to Resume",
            self.option_font,
            config.GOAL_COLOR_LEFT,
            config.SCREEN_WIDTH // 2,
            335,
        )

        draw_centered_text(
            surface,
            "Press R to Restart Match",
            self.option_font,
            config.GOAL_COLOR_RIGHT,
            config.SCREEN_WIDTH // 2,
            385,
        )

        draw_centered_text(
            surface,
            "Press M for Main Menu",
            self.option_font,
            config.HUD_TEXT_COLOR,
            config.SCREEN_WIDTH // 2,
            435,
        )