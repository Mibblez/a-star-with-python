import enum
from typing import List

import pygame

from sprites import *
from game_settings import *


class TileType(enum.Enum):
    FLOOR = 0
    WALL = 1
    NAV_START = 2
    NAV_END = 3
    NAV_PATH = 4
    NAV_OPEN_SET = 5
    NAV_CLOSED_SET = 6


class Tile(object):
    # Navigation point singletons
    nav_start = None
    nav_end = None

    def __init__(self, x_grid: int, y_grid: int, tile_type: TileType):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.walkable = True
        self.__tile_type = tile_type
        self.__sprite = None
        self.g_cost = -1            # Distance from the starting tile
        self.h_cost = -1            # Distance from the destination tile
        self.parent_tile = None     # Tile preceding this tile in nav path

    def __repr__(self) -> str:
        return f"{self.__tile_type.name} at: ({self.x_grid}, {self.y_grid})"

    @staticmethod
    def nav_start_exists() -> bool:
        if Tile.nav_start is None:
            return False
        else:
            return True

    @staticmethod
    def nav_end_exists() -> bool:
        if Tile.nav_end is None:
            return False
        else:
            return True

    @staticmethod
    def get_distance_between(tile1, tile2) -> int:
        x_distance = abs(tile1.x_grid - tile2.x_grid)
        y_distance = abs(tile1.y_grid - tile2.y_grid)

        if x_distance > y_distance:
            return 14 * y_distance + 10 * (x_distance - y_distance)
        else:
            return 14 * x_distance + 10 * (y_distance - x_distance)

    @property
    def f_cost(self):
        return self.g_cost + self. h_cost

    def get_pos(self) -> (int, int):
        return self.x_grid, self.y_grid

    def find_neighbors(self, game) -> list:
        neighbors: List[Tile] = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue    # Don't add self to neighbors

                check_x = self.x_grid + x
                check_y = self.y_grid + y

                if 0 <= check_x < game.WIDTH and 0 <= check_y < game.HEIGHT:
                    neighbors.append(game.grid[check_x][check_y])

        return neighbors

    def set_type(self, new_tile_type: TileType, game):
        # Do nothing if trying to set the tile's type to the same type
        if new_tile_type == self.__tile_type:
            return

        # Release singleton if removing nav start or nav end
        if self.__tile_type == TileType.NAV_START:
            Tile.nav_start = None
        elif self.__tile_type == TileType.NAV_END:
            Tile.nav_end = None

        # Remove old sprite if it exists
        if self.__sprite is not None:
            self.__sprite.kill()

        # I wish I had a switch
        if new_tile_type == TileType.WALL:
            self.__sprite = WallSprite(game, self.x_grid, self.y_grid)
            self.walkable = False
        elif new_tile_type == TileType.FLOOR:
            self.__sprite = None
            self.walkable = True
        elif new_tile_type == TileType.NAV_START:
            if Tile.nav_start is not None:
                Tile.nav_start.set_type(TileType.FLOOR, game)     # Set old nav_start tile to floor

            Tile.nav_start = self
            self.__sprite = NavStartSprite(game, self.x_grid, self.y_grid)
            self.walkable = True
        elif new_tile_type == TileType.NAV_END:
            if Tile.nav_end is not None:
                Tile.nav_end.set_type(TileType.FLOOR, game)       # Set old nav_end tile to floor

            Tile.nav_end = self
            self.__sprite = NavEndSprite(game, self.x_grid, self.y_grid)
            self.walkable = True
        elif new_tile_type == TileType.NAV_PATH:
            self.__sprite = NavPathSprite(game, self.x_grid, self.y_grid)
        elif new_tile_type == TileType.NAV_OPEN_SET:
            self.__sprite = OpenSetSprite(game, self.x_grid, self.y_grid)
        elif new_tile_type == TileType.NAV_CLOSED_SET:
            self.__sprite = ClosedSetSprite(game, self.x_grid, self.y_grid)

        self.__tile_type = new_tile_type

    def get_type(self) -> str:
        return self.__tile_type.name


class Game:
    def __init__(self, width: int, height: int, tile_size: int, title: str):
        pygame.init()
        pygame.display.set_caption(title)

        self.TILE_SIZE = tile_size
        self.WIDTH = width
        self.HEIGHT = height
        self.SCREEN_WIDTH = tile_size * width
        self.SCREEN_HEIGHT = tile_size * height
        self.screen = pygame.display.set_mode((self.SCREEN_HEIGHT, self.SCREEN_HEIGHT))

        self.grid: List[List[Tile]] = []
        self.can_modify_grid = True
        self.currently_pathfinding = False
        self.done_pathfinding = False

        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.nav_points = pygame.sprite.Group()

        # TODO: better variable name
        self.alternate_nav_start_end_replace = False

    def reset_grid(self):
        # Remove any tiles/sprites if they exist
        if self.grid:
            Tile.nav_start = None
            Tile.nav_end = None
            self.all_sprites.empty()
            self.obstacles.empty()
            self.nav_points.empty()
            self.grid.clear()

        # Populate grid with floor tiles
        for x in range(0, self.WIDTH):
            self.grid.append([])
            for y in range(0, self.HEIGHT):
                self.grid[x].append(Tile(x, y, TileType.FLOOR))

        self.can_modify_grid = True
        self.done_pathfinding = False

    def draw_grid(self):
        for x in range(0, self.SCREEN_WIDTH, self.TILE_SIZE):
            pygame.draw.line(self.screen, GREY, (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(0, self.SCREEN_HEIGHT, self.TILE_SIZE):
            pygame.draw.line(self.screen, GREY, (0, y), (self.SCREEN_WIDTH, y))

    def handle_input(self):
        # Get mouse position in grid
        mouse_pos_x_grid = pygame.mouse.get_pos()[0] // self.TILE_SIZE
        mouse_pos_y_grid = pygame.mouse.get_pos()[1] // self.TILE_SIZE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Check for key presses
            if event.type == pygame.KEYDOWN:
                # e -> examine tile under mouse
                if event.key == pygame.K_e:
                    print(self.grid[mouse_pos_x_grid][mouse_pos_y_grid])
                # SPACE -> start pathfinding or reset grid
                elif event.key == pygame.K_SPACE:
                    if not self.currently_pathfinding and not self.done_pathfinding:
                        if Tile.nav_start_exists() and Tile.nav_end_exists():
                            self.pathfind()
                        else:
                            print("Cannot pathfind. Both a start and an end tile need to exist.")
                    else:
                        self.reset_grid()
            # Check for mouse button presses
            elif event.type == pygame.MOUSEBUTTONDOWN and self.can_modify_grid:
                # LMB -> set start/end nav points
                if event.button == 1:
                    start_exists = Tile.nav_start_exists()
                    end_exists = Tile.nav_end_exists()

                    if not start_exists or (start_exists and end_exists and self.alternate_nav_start_end_replace):
                        self.grid[mouse_pos_x_grid][mouse_pos_y_grid].set_type(TileType.NAV_START, self)
                        self.alternate_nav_start_end_replace = False
                    else:
                        self.grid[mouse_pos_x_grid][mouse_pos_y_grid].set_type(TileType.NAV_END, self)
                        self.alternate_nav_start_end_replace = True

            # Actions to be repeated while button is held
            if self.can_modify_grid:
                mouse_buttons_pressed = pygame.mouse.get_pressed()
                # MMB -> change tile to floor
                if mouse_buttons_pressed[1]:
                    self.grid[mouse_pos_x_grid][mouse_pos_y_grid].set_type(TileType.FLOOR, self)
                # RMB -> change tile to wall
                elif mouse_buttons_pressed[2]:
                    self.grid[mouse_pos_x_grid][mouse_pos_y_grid].set_type(TileType.WALL, self)

    def pathfind(self):
        self.can_modify_grid = False
        self.currently_pathfinding = True

        start_tile = Tile.nav_start
        destination_tile = Tile.nav_end

        open_set: List[Tile] = []           # Tiles to be evaluated
        closed_set: List[Tile] = []         # Tiles that have already been evaluated

        open_set.append(start_tile)

        while len(open_set) > 0:
            current_tile = open_set[0]

            # Find tile in the open set with the lowest f_cost. If f_cost is the same, look at h_cost
            for i in range(1, len(open_set)):
                if (open_set[i].f_cost < current_tile.f_cost) or \
                        (open_set[i] == current_tile.f_cost and open_set[i].h_cost < current_tile.h_cost):
                    current_tile = open_set[i]

            # Move current_tile from open_set to closed_set
            open_set.remove(current_tile)
            closed_set.append(current_tile)

            if current_tile is destination_tile:    # Found destination
                self.show_sets(open_set, closed_set)
                self.find_path(start_tile, destination_tile)
                self.done_pathfinding = True
                self.currently_pathfinding = False
                return

            for neighbor_tile in current_tile.find_neighbors(self):
                if not neighbor_tile.walkable or neighbor_tile in closed_set:
                    continue

                new_move_cost = current_tile.g_cost + Tile.get_distance_between(current_tile, neighbor_tile)

                # Update neighbor's move cost and parent if it has not been evaluated or a better path has been found
                if new_move_cost < neighbor_tile.g_cost or neighbor_tile not in open_set:
                    neighbor_tile.g_cost = new_move_cost
                    neighbor_tile.h_cost = Tile.get_distance_between(neighbor_tile, destination_tile)
                    neighbor_tile.parent_tile = current_tile

                    if neighbor_tile not in open_set:
                        open_set.append(neighbor_tile)

        if self.currently_pathfinding:
            # Could not find a valid path
            self.show_sets(open_set, closed_set)
            self.currently_pathfinding = False
            self.done_pathfinding = True
            print("No valid path exists.")

    def find_path(self, start_tile, destination_tile):
        path: List[Tile] = []
        current_tile = destination_tile

        while current_tile is not start_tile:
            path.append(current_tile)
            current_tile = current_tile.parent_tile

        path.reverse()

        for tile in path:
            if tile is not Tile.nav_start and tile is not Tile.nav_end:
                tile.set_type(TileType.NAV_PATH, self)

    def show_sets(self, open_set, closed_set):
        for closed_tile in closed_set:
            # Do not change the type of the start or end tiles
            if closed_tile is Tile.nav_start or closed_tile is Tile.nav_end:
                continue
            closed_tile.set_type(TileType.NAV_CLOSED_SET, self)
        for open_tile in open_set:
            open_tile.set_type(TileType.NAV_OPEN_SET, self)

    # Game Loop
    def run(self):
        self.reset_grid()

        while self.running:
            self.handle_input()

            self.screen.fill(BLACK)
            self.all_sprites.draw(self.screen)
            self.draw_grid()

            pygame.display.update()

        pygame.quit()


a_star = Game(24, 24, 32, "A*")
a_star.run()
