import pygame
from game_settings import *


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((game.TILE_SIZE, game.TILE_SIZE))

        self.rect = self.image.get_rect()
        self.rect.x = x_grid * game.TILE_SIZE
        self.rect.y = y_grid * game.TILE_SIZE


class WallSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.obstacles)
        self.image.fill(WHITE)


class NavStartSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.nav_points)
        self.image.fill(CYAN)


class NavEndSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.nav_points)
        self.image.fill(DARK_CYAN)


class NavPathSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.nav_points)
        self.image.fill(ORANGE)


class OpenSetSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.nav_points)
        self.image.fill(GREEN)


class ClosedSetSprite(BaseSprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        super().__init__(game, x_grid, y_grid)

        self.groups.add(game.nav_points)
        self.image.fill(RED)
