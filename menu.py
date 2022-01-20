import pygame as pg

from util import blit_lines

MENU_TEXTS = [
    "click to start game",
    "press esc to exit game"
]
MENU_FONT_SIZE = 50
MENU_COLOR = (255, 255, 255)


def menu(screen: pg.Surface) -> str:
    '''display menu'''

    # blit menu background
    pg.draw.rect(screen, 'black', screen.get_rect())

    # blit menu texts
    blit_lines(
        screen,
        MENU_TEXTS,
        pg.font.Font(None, MENU_FONT_SIZE),
        MENU_COLOR
    )

    # update display
    pg.display.update()

    # check player operations
    while True:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                return 'startgame'
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return 'exitgame'
