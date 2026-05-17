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
from time import sleep


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
        self.CELL_SIZE = 40
        self.WIDTH = len(mapa.maze[0]) * self.CELL_SIZE
        self.HEIGHT = len(mapa.maze) * self.CELL_SIZE

    def __put_pixel(self, col: tuple[int, int, int, int],
                    idx: int) -> None:
        self.data[idx] = col[0]
        self.data[idx + 1] = col[1]
        self.data[idx + 2] = col[2]
        self.data[idx + 3] = col[3]

    def __put_walls(self, v: Cell, idx: int) -> None:
        if CellType.FORTY_TWO in v.cell_type:
            self.__put_pixel(self.ALL_COLORS.get_color(
                ColorCell.WALL_42.value), idx)
        else:
            self.__put_pixel(self.ALL_COLORS.get_color(
                ColorCell.WALL.value), idx)

    def __draw_maze(self) -> None:
        for y in range(self.ROWS):
            for x in range(self.COLS):
                v = self.mapa[y][x]
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                for dy in range(self.CELL_SIZE):
                    for dx in range(self.CELL_SIZE):
                        idx = (py + dy) * self.size_line + (px + dx) * 4
                        if CellType.FORTY_TWO in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.FLOOR_42.value), idx)
                        elif CellType.ENTRY in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.ENTRY.value), idx)
                        elif CellType.EXIT in v.cell_type:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.EXIT.value), idx)
                        else:
                            self.__put_pixel(self.ALL_COLORS.get_color(
                                ColorCell.FLOOR.value), idx)

                if v.walls.north:
                    for dx in range(self.CELL_SIZE):
                        idx = py * self.size_line + (px + dx) * 4
                        self.__put_walls(v, idx)

                if v.walls.east:
                    for dy in range(self.CELL_SIZE):
                        idx = (py + dy) * self.size_line + (
                               (px + self.CELL_SIZE - 1) * 4)
                        self.__put_walls(v, idx)

                if v.walls.south:
                    for dx in range(self.CELL_SIZE):
                        idx = (py + self.CELL_SIZE - 1) * self.size_line + (
                            (px + dx) * 4)
                        self.__put_walls(v, idx)

                if v.walls.west:
                    for dy in range(self.CELL_SIZE):
                        idx = (py + dy) * self.size_line + px * 4
                        self.__put_walls(v, idx)

    def __key_how(self, key: int, param: Mlx) -> None:
        if key in (49, 50, 51, 52, 53):
            if key == 49:
                self.ALL_COLORS.all_colors()
            if key == 50:
                dic = lector(argv[1])
                if not isinstance(dic.get("SEED"), str):
                    self.maze.data.SEED = randint(1, maxs)
                    self.mapa = MazeGenerator(self.maze.data).maze
                    self.content = self.maze.solution
            self.__draw_maze(self.data, self.size_line)
            if key == 51:
                for i in self.maze.data.algoritm["algoritm"]():
                    self.content = self.maze.solution
                    self.m.mlx_put_image_to_window(self.m.mlx_ptr,
                                                self.win, self.img, 10, 10)
                    self.__drawway(self.__obtencoord(self.maze.data.ENTRY, self.maze.data.EXIT, self.content))
                    sleep(0.0625)
            if key == 52:
                for _ in self.maze.data.algoritm["algoritm"]():
                    ...
                self.content = self.maze.data.algoritm["list"]()
            self.m.mlx_put_image_to_window(self.m.mlx_ptr,
                                           self.win, self.img, 10, 10)
            self.__drawway(self.__obtencoord(self.maze.data.ENTRY, self.maze.data.EXIT, self.content))
        if key == 65307:
            param.mlx_loop_exit(param.mlx_ptr)

    def __obtencoord(self, enter: tuple[int, int], exit: tuple[int, int], direc: str | list[str]) -> set[tuple[int, int]]:
        movements = {
            "N": (0, -1),
            "W": (-1, 0),
            "S": (0, 1),
            "E": (1, 0)
        }
        sol = set()
        if isinstance(direc, list):
            for stri in direc:
                sol.add(self._obtencoord(enter, exit, stri))
            return sol
        x, y = enter
        finx, finy = exit
        for i in direc:
            opex, opey = movements[i]
            x += opex
            y += opey
            if not (x, y) in sol:
                sol.add((x, y))
            else:
                x -= opex
                y -= opey     
        return sol
    
    def __drawway(self, long: set[tuple[int, int]]) -> None:
        for x, y in long:
            v = self.mapa[y][x]
            px = (x * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)
            py = (y * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)

            for dy in range(int(self.CELL_SIZE * 0.7)):
                for dx in range(int(self.CELL_SIZE * 0.7)):
                    idx = (py + dy) * self.size_line + (px + dx) * 4
                    self.__put_pixel(self.ALL_COLORS.get_color(
                        ColorCell.WAY.value), idx)
    
    def visualizer(self) -> None:
        self.m = Mlx()
        self.m.mlx_ptr = self.m.mlx_init()
        win = self.m.mlx_new_window(self.m.mlx_ptr,
                                         self.WIDTH + 20,
                                         self.HEIGHT + 20,
                                         "Laberinto")
        img = self.m.mlx_new_image(self.m.mlx_ptr, self.WIDTH,
                                        self.HEIGHT)

        self.data, _, self.size_line, _ = self.m.mlx_get_data_addr(img)

        self.content = self.maze.solution
        self.__draw_maze()
        self.__drawway(self.__obtencoord(self.maze.data.ENTRY, self.maze.data.EXIT, self.content))

        self.m.mlx_put_image_to_window(self.m.mlx_ptr, win,
                                       img, 10, 10)
        self.m.mlx_key_hook(win, self.__key_how, self.m)
        self.m.mlx_loop(self.m.mlx_ptr)
