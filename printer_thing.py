from typing import Any
from random import randint
from sys import argv, maxsize as maxs
from time import sleep
from mlx import Mlx
from maze.cell import Cell
from maze.enums import CellType
from colors import All_colors, ColorCell
from parser_config import lector
from maze.maze_generator import MazeGenerator

class Drawer():

    maze: MazeGenerator
    WIDTH: int
    HEIGHT: int
    CELL_SIZE: int
    ALL_COLORS = All_colors()
    m: Mlx

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze = maze
        self.CELL_SIZE = 40
        self.WIDTH = maze.data.WIDTH * self.CELL_SIZE
        self.HEIGHT = maze.data.HEIGHT * self.CELL_SIZE

    def __put_pixel(
            self,
            col: tuple[int, int, int, int],
            idx: int
    ) -> None:
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

    def __print_background(self, py: int, px: int, v: Cell):
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

    def __draw_maze(self) -> None:
        for y in range(self.maze.data.HEIGHT):
            for x in range(self.maze.data.WIDTH):
                v = self.maze.maze[y][x]
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                self.__print_background(py, px, v)

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
                    self.maze = MazeGenerator(self.maze.data)
                    self.content = self.maze.solution
            if key == 51:
                self.__draw_maze()
                for i in self.maze.algoritm["algoritm"]():
                    self.content = i
                    cord = self.__obtencoord(
                        self.maze.data.ENTRY,
                        self.maze.data.EXIT,
                        self.content
                    )
                    self.__drawway(cord)
                    self.mlx.mlx_put_image_to_window(
                        self.mlx.mlx_ptr,
                        self.win,
                        self.img,
                        10,
                        10
                    )
                    self.mlx.mlx_do_sync(self.mlx.mlx_ptr)
                    self.__undrawway(cord)
                    sleep(0.03125)
                self.content = self.maze.solution
            if key == 52:
                for i in self.maze.algoritm["algoritm"]():
                    pass
                if len(self.maze.algoritm["list"]()) != 0:
                    self.solution = self.maze.algoritm["sorter"]()
            self.__draw_maze()
            self.__drawway(self.__obtencoord(
                self.maze.data.ENTRY,
                self.maze.data.EXIT,
                self.content
            ))
            self.mlx.mlx_put_image_to_window(
                self.mlx.mlx_ptr,
                self.win,
                self.img,
                10,
                10
            )
        if key == 65307:
            param.mlx_loop_exit(param.mlx_ptr)

    def __obtencoord(
            self,
            enter: tuple[int, int],
            exit: tuple[int, int],
            direc: str | list[str]
    ) -> set[tuple[int, int]]:
        movements = {
            "N": (0, -1),
            "W": (-1, 0),
            "S": (0, 1),
            "E": (1, 0)
        }
        sol = set()
        if isinstance(direc, list):
            for stri in direc:
                sol.update(self.__obtencoord(enter, exit, stri))
            return sol
        x, y = enter
        enx, eny = enter
        finx, finy = exit
        for i in direc:
            opex, opey = movements[i]
            x += opex
            y += opey
            if not (finx == x and y == finy) and not (enx == x and y == eny):
                if not (x, y) in sol:
                    sol.add((x, y))
                else:
                    x -= opex
                    y -= opey
        return sol

    def __drawway(self, long: set[tuple[int, int]]) -> None:
        for x, y in long:
            px = (x * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)
            py = (y * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)

            for dy in range(int(self.CELL_SIZE * 0.7)):
                for dx in range(int(self.CELL_SIZE * 0.7)):
                    idx = (py + dy) * self.size_line + (px + dx) * 4
                    self.__put_pixel(self.ALL_COLORS.get_color(
                        ColorCell.WAY.value), idx)

    def __undrawway(self, long: set[tuple[int, int]]) -> None:
        for x, y in long:
            px = (x * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)
            py = (y * self.CELL_SIZE) + int(self.CELL_SIZE * 0.15)

            for dy in range(int(self.CELL_SIZE * 0.7)):
                for dx in range(int(self.CELL_SIZE * 0.7)):
                    idx = (py + dy) * self.size_line + (px + dx) * 4
                    self.__put_pixel(self.ALL_COLORS.get_color(
                        ColorCell.FLOOR.value), idx)

    def visualizer(self) -> None:
        self.mlx = Mlx()
        self.mlx.mlx_ptr = self.mlx.mlx_init()
        self.win = self.mlx.mlx_new_window(
            self.mlx.mlx_ptr,
            self.WIDTH + 20,
            self.HEIGHT + 20,
            "Maze"
        )
        self.img = self.mlx.mlx_new_image(
            self.mlx.mlx_ptr,
            self.WIDTH,
            self.HEIGHT
        )
        [
            self.data, _,
            self.size_line, _
        ] = self.mlx.mlx_get_data_addr(self.img)
        self.content = self.maze.solution
        self.__draw_maze()
        self.__drawway(self.__obtencoord(
            self.maze.data.ENTRY,
            self.maze.data.EXIT,
            self.content
        ))

        self.mlx.mlx_put_image_to_window(
            self.mlx.mlx_ptr,
            self.win,
            self.img,
            10,
            10
        )
        self.mlx.mlx_key_hook(self.win, self.__key_how, self.mlx)
        self.mlx.mlx_loop(self.mlx.mlx_ptr)
