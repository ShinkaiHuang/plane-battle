import pygame as pg

from menu  import menu
from game  import game
from scoreboard import scoreboard

SCREEN_SIZE = 750, 750


def main() -> None:
    '''main function of the game'''
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(SCREEN_SIZE)
    while True:
        state = menu(screen) # display menu
        if state == 'exitgame': # player exit game in menu
            return
        elif state == 'startgame': # player start game in menu
            game_max_score, player_score, state = game(screen, clock) # player play game
            if state == 'exitgame': # player exit game during game
                return
            elif state == 'win' or 'lose': # game end
                state = scoreboard(screen, game_max_score, player_score, state)
                if state == 'startgame':
                    continue
                elif state == 'exitgame':
                    return

if __name__ == "__main__":
    main()