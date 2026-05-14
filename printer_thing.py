from mlx import Mlx
from maze.cell import Cell
from maze.enums import CellType
from colors import All_colors, ColorCell
from parser_config import lector
from maze.maze_generator import MazeGenerator
from typing import Any
from random import randint
from sys import argv
from sys import maxsize as maxs


class Drawer():

    maze: MazeGenerator
    mapa: list[list[Cell]]
    ROWS: int
    COLS: int
    WIDTH: int
    HEIGHT: int
    CELL_SIZE: int
    ALL_COLORS = All_colors()
    m: Mlx

    def __init__(self, mapa: MazeGenerator) -> None:
        self.maze = mapa
        self.mapa = mapa.maze
        self.ROWS = len(mapa.maze)
        self.COLS = len(mapa.maze[0])
        self.CELL_SIZE = 20
        self.WIDTH = len(mapa.maze[0]) * self.CELL_SIZE
        self.HEIGHT = len(mapa.maze) * self.CELL_SIZE

    def __put_pixel(self, col: tuple[int, int, int, int], data: list[Any],
                    idx: int) -> None:
        data[idx] = col[0]
        data[idx + 1] = col[1]
        data[idx + 2] = col[2]
        data[idx + 3] = col[3]

    def __put_walls(self, v: Cell, data: list[Any], idx: int) -> None:
        if CellType.FORTY_TWO in v.cell_type:
            self.__put_pixel(self.ALL_COLORS.get_color(
                ColorCell.WALL_42.value), data, idx)
        else:
            self.__put_pixel(self.ALL_COLORS.get_color(
                ColorCell.WALL.value), data, idx)

    def __draw_maze(self, data: list[Any], size_line: int) -> None:
        for y in range(self.ROWS):
            for x in range(self.COLS):
                v = self.mapa[y][x]
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                for dy in range(self.CELL_SIZE):
                    for dx in range(self.CELL_SIZE):
                        idx = (py + dy) * size_line + (px + dx) * 4
                        if CellType.FORTY_TWO in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.FLOOR_42.value), data, idx)
                        elif CellType.ENTRY in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.ENTRY.value), data, idx)
                        elif CellType.EXIT in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.EXIT.value), data, idx)
                        else:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.FLOOR.value), data, idx)

                if v.walls.north:
                    for dx in range(self.CELL_SIZE):
                        idx = py * size_line + (px + dx) * 4
                        self.__put_walls(v, data, idx)

                if v.walls.east:
                    for dy in range(self.CELL_SIZE):
                        idx = (py + dy) * size_line + (
                               (px + self.CELL_SIZE - 1) * 4)
                        self.__put_walls(v, data, idx)

                if v.walls.south:
                    for dx in range(self.CELL_SIZE):
                        idx = (py + self.CELL_SIZE - 1) * size_line + (
                            (px + dx) * 4)
                        self.__put_walls(v, data, idx)

                if v.walls.west:
                    for dy in range(self.CELL_SIZE):
                        idx = (py + dy) * size_line + px * 4
                        self.__put_walls(v, data, idx)

    def _key_how(self, key: int, param: Mlx) -> None:
        if key in (49, 50, 51, 52, 53):
            if key == 49:
                self.ALL_COLORS.all_colors()
            if key == 50:
                dic = lector(argv[1])
                if isinstance(dic.get("SEED"), str):
                    self.maze.data.SEED = randint(1, maxs)
                    self.mapa = MazeGenerator(self.maze.data).maze
                    return
            self.__draw_maze(self.data, self.size_line)
            self.m.mlx_put_image_to_window(self.m.mlx_ptr,
                                           self.win, self.img, 10, 10)
        if key == 65307:
            param.mlx_loop_exit(param.mlx_ptr)

    def visualizer(self) -> None:
        self.m = Mlx()
        self.m.mlx_ptr = self.m.mlx_init()
        self.win = self.m.mlx_new_window(self.m.mlx_ptr,
                                         self.WIDTH + 20,
                                         self.HEIGHT + 20,
                                         "Laberinto")
        self.img = self.m.mlx_new_image(self.m.mlx_ptr, self.WIDTH,
                                        self.HEIGHT)

        self.data, _, self.size_line, _ = self.m.mlx_get_data_addr(self.img)

        self.__draw_maze(self.data, self.size_line)

        self.m.mlx_put_image_to_window(self.m.mlx_ptr, self.win,
                                       self.img, 10, 10)
        self.m.mlx_key_hook(self.win, self._key_how, self.m)
        self.m.mlx_loop(self.m.mlx_ptr)
