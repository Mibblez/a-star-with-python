import pygame
from game_settings import *


class WallSprite(pygame.sprite.Sprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        self.groups = game.all_sprites, game.obstacles
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((game.TILE_SIZE, game.TILE_SIZE))
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = x_grid * game.TILE_SIZE
        self.rect.y = y_grid * game.TILE_SIZE


class NavPointSprite(pygame.sprite.Sprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        self.groups = game.all_sprites, game.nav_points
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((game.TILE_SIZE, game.TILE_SIZE))
        self.image.fill(CYAN)

        self.rect = self.image.get_rect()
        self.rect.x = x_grid * game.TILE_SIZE
        self.rect.y = y_grid * game.TILE_SIZE


class NavPathSprite(pygame.sprite.Sprite):
    def __init__(self, game, x_grid: int, y_grid: int):
        self.groups = game.all_sprites, game.nav_points
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.Surface((game.TILE_SIZE, game.TILE_SIZE))
        self.image.fill(ORANGE)

        self.rect = self.image.get_rect()
        self.rect.x = x_grid * game.TILE_SIZE
        self.rect.y = y_grid * game.TILE_SIZE