import pygame as pg

import os


def blit_lines(target_surface: pg.Surface, texts: list[str], font_: pg.font.Font, color: tuple) -> list[pg.rect.Rect]:
    '''display strings line by line in the middle of target surface'''

    # (blit_x, blit_y) is the blit position
    font_height = font_.get_height()
    blit_y = (target_surface.get_height() - font_height * len(texts)) // 2
    rects = []
    surface_width = target_surface.get_width()
    for text in texts:

        # as for font, use convert_alpha() instead of convert() to preserve transparency, or use neither since it will be adapted to the screen later
        text_surface = font_.render(text, True, color).convert_alpha()

        # blit in the middle of the target surface
        blit_x = (surface_width - text_surface.get_width()) // 2
        rects.append(
            target_surface.blit(text_surface, (blit_x, blit_y))
        )
        blit_y += font_height  # update blit position

    return rects


def images_to_surfaces(screen, foldername: str, filenames: str) -> list[pg.Surface]:
    '''load image and generate converted surface'''
    surfaces = []

    for filename in filenames:
        # absolute path of the image
        abspath = os.path.join(
            os.path.split(os.path.abspath(__file__))[0],
            foldername,
            filename
        )

        # generate surface
        surface = pg.image.load(abspath).convert()
        surface.set_colorkey(surface.get_at((0, 0)))

        surfaces.append(surface)

    return surfaces
