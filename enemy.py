import pygame as pg

import random

from util import images_to_surfaces

ENEMY_IMGS_FOLDER = 'asset'
ENEMY_IMGS = ['alien1.gif', 'alien2.gif', 'alien3.gif']
DEFAULT_GEN_PROB = 0.3
DEFAULT_GEN_POS_Y = 0.002
DEFAULT_GEN_SPEED = 0.005

class Enemy(pg.sprite.Sprite):
    '''game enemy'''

    surfaces = []
    screen = pg.Surface((0,0))

    def __init__(
        self, 
        born_speed: tuple[float], 
        born_pos: tuple[float], 
        *groups: pg.sprite.AbstractGroup
    ):
        super().__init__(*groups)
        self.speed = born_speed
        self.image = random.choice(Enemy.surfaces)  # type of self.image is Surface
        self.rect = self.image.get_rect().move(born_pos)

    def update(self):
        self.rect.move_ip(self.speed)
        if self.rect.x < Enemy.screen.get_rect().left:
            self.speed[0] = abs(self.speed[0])
        elif self.rect.x > Enemy.screen.get_rect().right:
            self.speed[0] = -abs(self.speed[0])
        if self.rect.y < Enemy.screen.get_rect().top:
            self.speed[1] = abs(self.speed[1])
        elif self.rect.y > Enemy.screen.get_rect().bottom:
            self.kill()

    @staticmethod
    def random_gen(
        screen: pg.Surface, 
        *groups: pg.sprite.AbstractGroup, 
        born_prob: float = 0, 
        born_speed: list[float] = [], 
        born_pos: list[float] = []
    ):
        '''generate an Enemy, may randomly not generate'''
        
        if Enemy.surfaces == []: # Enemy class uninitialize
            Enemy.surfaces = images_to_surfaces(screen, ENEMY_IMGS_FOLDER, ENEMY_IMGS)
            Enemy.screen = screen
        
        if born_prob == 0:
            born_prob = DEFAULT_GEN_PROB
        
        if random.random() < born_prob:
            if born_pos == []:
                born_pos = [
                    random.random() * screen.get_rect().width, 
                    -screen.get_rect().height * DEFAULT_GEN_POS_Y
                ]
            
            if born_speed == []:
                born_speed = [
                    random.random() * 2 * screen.get_rect().width * DEFAULT_GEN_SPEED - screen.get_rect().width * DEFAULT_GEN_SPEED,
                    random.random() * screen.get_rect().height * DEFAULT_GEN_SPEED
                ]
                
            Enemy(born_speed, born_pos, *groups)
