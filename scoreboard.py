import pygame as pg

from util import blit_lines
from menu import MENU_TEXTS

SCORE_FONT_SIZE = 50
SCORE_COLOR = (255, 255, 255)


def scoreboard(screen: pg.Surface, game_max_score: int, player_score: int, state: str) -> str:
    '''display score board'''

    # blit scoreboard background
    pg.draw.rect(screen, 'black', screen.get_rect())

    # blit scoreboard text
    score_texts = [
        'You {}'.format(state),
        'Got {}% sorce - {} / {}'.format(
            player_score * 100 / game_max_score, 
            str(player_score), 
            str(game_max_score)
        )
    ] + MENU_TEXTS
    blit_lines(
        screen,
        score_texts,
        pg.font.Font(None, SCORE_FONT_SIZE),
        SCORE_COLOR
    )

    # update display
    pg.display.update()

    # check player operations
    while True:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return 'exitgame'
            elif event.type == pg.MOUSEBUTTONDOWN:
                return 'startgame'
