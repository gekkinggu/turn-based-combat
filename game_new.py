# python
"""game_new.py

Game module for the turn-based combat system.
"""

from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class Game:
    """Game class for the turn-based combat system."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()


WIDTH = 800
HEIGHT = 600
CAPTION = "Game"
pygame.init()
pygame.display.set_caption(CAPTION)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game = Game(screen)

while True:
    dt = game.clock.tick(60) / 1000  # Delta time in seconds.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    game.screen.fill((0, 0, 0))  # Clear screen with black.
    pygame.display.flip()