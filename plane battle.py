import random
import os
import pygame as pg


# game constants
ENEMY_SHOWUP_ODDS = 22  # chances a new enemy appears
ENEMY_BOMB_ODDS = 60  # chances a new bomb will drop
ENEMY_RELOAD = 12  # frames between new enemys
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCORE = 0
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(MAIN_DIR, "asset", file)
    surface = pg.image.load(file).convert()
    surface.set_colorkey(surface.get_at((0,0)))
    return surface

def load_sound(file):
    file = os.path.join(MAIN_DIR, "asset", file)
    sound = pg.mixer.Sound(file)
    return sound


class Player(pg.sprite.Sprite):
    speed = 10
    bounce = 24
    supershot_num = 50
    gun_offset = -11
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, horizontal, vertical):
        self.rect.move_ip(horizontal * self.speed, vertical * self.speed)
        self.rect = self.rect.clamp(SCREENRECT)
        # self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Enemy(pg.sprite.Sprite):
    speed = 10
    animcycle = 12
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Enemy.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]
 

class Explosion(pg.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Shot(pg.sprite.Sprite):
    speed = -11
    images = []

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class SuperShot(Shot):
    speed = -5
    images = []

    def __init__(self, pos):
        Shot.__init__(self, pos)


class EnemyBomb(pg.sprite.Sprite):
    speed = 7
    images = []

    def __init__(self, enemy):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=enemy.rect.move(0, 5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.font = pg.font.Font(None, 60)
        self.font.set_italic(1)
        self.color = "white"
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 430)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)


def game():
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    img = load_image("plane.png")
    Player.images = [img, pg.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]
    Enemy.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    EnemyBomb.images = [load_image("bomb.gif")]
    Shot.images = [load_image("shot.gif")]
    SuperShot.images = [load_image("super_shot.png")]

    # decorate the game window
    icon = pg.transform.scale(Enemy.images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("plane battle")
    pg.mouse.set_visible(0)

    # create the background
    bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pg.mixer:
        music = os.path.join(MAIN_DIR, "asset", "house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    # Initialize Game Groups
    enemies = pg.sprite.Group()
    shots = pg.sprite.Group()
    supershots = pg.sprite.Group()
    enemybombs = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastenemy = pg.sprite.GroupSingle()

    # assign default groups to each sprite class
    Player.containers = all
    Enemy.containers = enemies, all, lastenemy
    Shot.containers = shots, all
    SuperShot.containers = supershots, all
    EnemyBomb.containers = enemybombs, all
    Explosion.containers = all
    Score.containers = all

    # Create Some Starting Values
    enemyreload = ENEMY_RELOAD
    clock = pg.time.Clock()

    # initialize our starting sprites
    global SCORE
    player = Player()
    Enemy()
    if pg.font:
        all.add(Score())

    # guidence menu
    game_tips = []
    game_tip = pg.font.Font(None, 30).render(
        "click to start",
        True,
        (255, 255, 255)
    )
    game_tips.append(game_tip)
    game_tip = pg.font.Font(None, 30).render(
        "prese space to shoot",
        True,
        (255, 255, 255)
    )
    game_tips.append(game_tip)
    game_tip = pg.font.Font(None, 30).render(
        "prese X to make super attack",
        True,
        (255, 255, 255)
    )
    game_tips.append(game_tip)
    game_tip = pg.font.Font(None, 30).render(
        "prese F to convert to full screen",
        True,
        (255, 255, 255)
    )
    game_tips.append(game_tip)
    game_tip = pg.font.Font(None, 30).render(
        "prese esc to quit",
        True,
        (255, 255, 255)
    )
    game_tips.append(game_tip)
    
    # main loop
    gaming = False
    while SCORE < 20:
        if not gaming:
            # memu
            game_tips_rect = []
            for idx, game_tip in enumerate(game_tips):
                game_tip_rect = screen.blit(game_tip, (100, screen.get_height() // 2 + idx * game_tip.get_height()))
                game_tips_rect.append(game_tip_rect)
            pg.display.update(game_tips_rect)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    gaming = True
                    screen.blit(background,(0,0))
                    pg.display.update(game_tips_rect)

        else:
            if not player.alive():
                SCORE = 0
                break

            # get input
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        pause = True
                        continue
                    elif event.key == pg.K_f:
                        if not fullscreen:
                            print("Changing to FULLSCREEN")
                            screen_backup = screen.copy()
                            screen = pg.display.set_mode(
                                SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                            )
                            screen.blit(screen_backup, (0, 0))
                        else:
                            print("Changing to windowed mode")
                            screen_backup = screen.copy()
                            screen = pg.display.set_mode(
                                SCREENRECT.size, winstyle, bestdepth
                            )
                            screen.blit(screen_backup, (0, 0))
                        pg.display.flip()
                        fullscreen = not fullscreen

            keystate = pg.key.get_pressed()

            # clear/erase the last drawn sprites
            all.clear(screen, background)

            # update all the sprites
            all.update()

            # handle player input
            horizontal = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
            vertical = keystate[pg.K_DOWN] - keystate[pg.K_UP]
            player.move(horizontal,vertical)
            firing = keystate[pg.K_SPACE]
            if not player.reloading and firing:
                Shot(player.gunpos())
                if pg.mixer:
                    shoot_sound.play()
            supershoting = keystate[pg.K_x]
            if not player.reloading and supershoting and player.supershot_num > 0:
                SuperShot(player.gunpos())
                player.supershot_num -= 1
                if pg.mixer:
                    shoot_sound.play()
            player.reloading = firing or supershoting

            # Create new enemy
            if enemyreload:
                enemyreload = enemyreload - 1
            elif not int(random.random() * ENEMY_SHOWUP_ODDS):
                Enemy()
                enemyreload = ENEMY_RELOAD

            # Drop bombs
            if lastenemy and not int(random.random() * ENEMY_BOMB_ODDS):
                EnemyBomb(lastenemy.sprite)

            # Detect collisions between enemies and players.
            for enemy in pg.sprite.spritecollide(player, enemies, 1):
                if pg.mixer:
                    boom_sound.play()
                Explosion(enemy)
                Explosion(player)
                SCORE += 7
                player.kill()

            # See if shots hit the enemies.
            for enemy in pg.sprite.groupcollide(enemies, shots, 1, 1).keys():
                if pg.mixer:
                    boom_sound.play()
                Explosion(enemy)
                SCORE += 7
            
            # See if supershots hit the enemies.
            for enemy in pg.sprite.groupcollide(enemies, supershots, 1, 0).keys():
                if pg.mixer:
                    boom_sound.play()
                Explosion(enemy)
                SCORE += 7

            # See if enemy bombs hit the player.
            for bomb in pg.sprite.spritecollide(player, enemybombs, 1):
                if pg.mixer:
                    boom_sound.play()
                Explosion(player)
                Explosion(bomb)
                player.kill()

            # draw the scene
            dirty = all.draw(screen)
            pg.display.update(dirty)

            clock.tick(60)


    boss = Boss()
    while True:
        if not boss.alive():
            break
        if not player.alive():
            SCORE = 0
            break
    
        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    pause = True
                    continue
                elif event.key == pg.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    fullscreen = not fullscreen

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        horizontal = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        vertical = keystate[pg.K_DOWN] - keystate[pg.K_UP]
        player.move(horizontal,vertical)
        firing = keystate[pg.K_SPACE]
        if not player.reloading and firing:
            Shot(player.gunpos())
            if pg.mixer:
                shoot_sound.play()
        supershoting = keystate[pg.K_x]
        if not player.reloading and supershoting and player.supershot_num > 0:
            SuperShot(player.gunpos())
            player.supershot_num -= 1
            if pg.mixer:
                shoot_sound.play()
        player.reloading = firing or supershoting

        
        

        # Drop bombs
        if lastenemy and not int(random.random() * ENEMY_BOMB_ODDS):
            BossBomb(lastenemy.sprite)


        # See if shot hit the boss.
        for shot in pg.sprite.spritecollide(boss, shots, 1):
            if pg.mixer:
                boom_sound.play()
            boss.reduce_health()
            Explosion(bomb)

        # See if enemy bombs hit the player.
        for bomb in pg.sprite.spritecollide(player, bossbombs, 1):
            if pg.mixer:
                boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        # draw the scene
        dirty = all.draw(screen)
        pg.display.update(dirty)
        clock.tick(60)

    while True:
        game_win = pg.font.Font(None, 60).render(
            "YOU WIN!",
            True,
            (255, 255, 255)
        )
        gamewin_rect = screen.blit(game_win,(10,screen.get_height()//2))
        pg.display.update(gamewin_rect)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)

def main():
    running = True
    while running != False:
        running = game()


if __name__ == "__main__":
    main()
    pg.quit()
