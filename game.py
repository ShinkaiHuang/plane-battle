import pygame as pg

from enemy import Enemy

FPS = 60

def game(screen: pg.Surface, clock: pg.time.Clock) -> tuple:
    '''
    Player gaming.
    Return maximum score of the game, player score, game end state(win, lose, exitgame)
    '''
    enemies = pg.sprite.Group()
    allsprite = pg.sprite.RenderUpdates()
    background = pg.Surface(screen.get_size())
    screen.blit(background, (0,0))
    pg.display.update()
    while True:
        clock.tick(FPS)
        allsprite.clear(screen, background)
        Enemy.random_gen(screen, (enemies, allsprite))
        rects = allsprite.draw(screen)
        pg.display.update(rects)
        enemies.update()

    return 100, 90, 'win'
