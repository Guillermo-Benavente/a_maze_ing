from typing import Any
from random import randint
from sys import argv, maxsize as maxs
from time import sleep
from collections import deque
from mlx import Mlx
from mlx_py import MlxPy, FlatCanvas
from maze.cell import Cell
from maze.enums import CellType
from colors import All_colors, ColorCell
from parser_config import lector
from maze.maze_generator import MazeGenerator

class Drawer():

    WIDTH: int
    HEIGHT: int
    CELL_SIZE: int
    ALL_COLORS = All_colors()
    MOVEMENTS = {
        "N": (0, -1),
        "W": (-1, 0),
        "S": (0, 1),
        "E": (1, 0)
    }
    MARGIN: int = 10
    maze: MazeGenerator
    mlx: MlxPy

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
        self.mlx.flat_canvas.bytes[idx] = col[0]
        self.mlx.flat_canvas.bytes[idx + 1] = col[1]
        self.mlx.flat_canvas.bytes[idx + 2] = col[2]
        self.mlx.flat_canvas.bytes[idx + 3] = col[3]

    def __get_cell_color(self, cell: Cell, is_wall: bool = False) -> tuple[int, int, int, int]:
        if CellType.FORTY_TWO in cell.cell_type:
            return self.ALL_COLORS.get_color(ColorCell.WALL_42.value if is_wall else ColorCell.FLOOR_42.value)
        if is_wall:
            return self.ALL_COLORS.get_color(ColorCell.WALL.value)
        if CellType.ENTRY in cell.cell_type:
            return self.ALL_COLORS.get_color(ColorCell.ENTRY.value)
        if CellType.EXIT in cell.cell_type:
            return self.ALL_COLORS.get_color(ColorCell.EXIT.value)
        return self.ALL_COLORS.get_color(ColorCell.FLOOR.value)

    def __draw_special_tiles(self) -> None:
        for x, y, cell in self.maze.special_cells:
            origin_x = x * self.CELL_SIZE
            origin_y = y * self.CELL_SIZE
            floor_color = self.__get_cell_color(cell, False)
            self.mlx.flat_canvas.draw_rectangle(
                origin_x, origin_y, 
                self.CELL_SIZE, self.CELL_SIZE, 
                floor_color
            )

    def __draw_maze(self) -> None:
        canvas: FlatCanvas = self.mlx.flat_canvas
        default_floor = self.ALL_COLORS.get_color(ColorCell.FLOOR.value)
        canvas.fill_all(
            self.maze.data.WIDTH * self.CELL_SIZE, 
            self.maze.data.HEIGHT * self.CELL_SIZE, 
            default_floor
        )
        self.__draw_special_tiles()
        for y in range(self.maze.data.HEIGHT):
            for x in range(self.maze.data.WIDTH):
                cell = self.maze.maze[y][x]
                origin_x = x * self.CELL_SIZE
                origin_y = y * self.CELL_SIZE
                wall_color = self.__get_cell_color(cell, True)
                if cell.walls.north:
                    canvas.draw_horizontal_line(
                        origin_x,
                        origin_y,
                        self.CELL_SIZE,
                        wall_color
                    )
                if cell.walls.west:
                    canvas.draw_vertical_line(
                        origin_x,
                        origin_y,
                        self.CELL_SIZE,
                        wall_color
                    )
                if cell.walls.south:
                    canvas.draw_horizontal_line(
                        origin_x,
                        origin_y + self.CELL_SIZE - 1,
                        self.CELL_SIZE,
                        wall_color
                    )
                if cell.walls.east:
                    canvas.draw_vertical_line(
                        origin_x + self.CELL_SIZE - 1,
                        origin_y,
                        self.CELL_SIZE,
                        wall_color
                    )

    def __key_how(self, key: int, mlx_param: Mlx) -> None:
        if key in (49, 50, 51, 52, 53):
            if key == 49:
                self.ALL_COLORS.all_colors()
            elif key == 50:
                config_data = lector(argv[1])
                if not isinstance(config_data.get("SEED"), str):
                    self.maze.data.SEED = randint(1, maxs)
                    self.maze = MazeGenerator(self.maze.data)
                    self.content = self.maze.solution
            elif key == 51:
                self.__draw_maze()
                for algorithm_step in self.maze.algorithm["algorithm"]():
                    self.content = algorithm_step
                    path_coords = self.__get_path_coords(
                        self.maze.data.ENTRY,
                        self.maze.data.EXIT,
                        self.content
                    )
                    self.__drawway(path_coords)
                    self.mlx.mlx_put_image_to_window(self.MARGIN)
                    self.mlx.mlx_do_sync()
                    self.__undrawway(path_coords)
                    sleep(0.03125)
                self.content = self.maze.solution
            elif key == 52:
                deque(self.maze.algorithm["algorithm"](), maxlen=0)
                if len(self.maze.algorithm["list"]()) != 0:
                    self.solution = self.maze.algorithm["sorter"]()
            self.__draw_maze()
            self.__drawway(self.__get_path_coords(
                self.maze.data.ENTRY,
                self.maze.data.EXIT,
                self.content
            ))
            self.mlx.mlx_put_image_to_window(self.MARGIN)
        if key in (65307):
            mlx_param.mlx_loop_exit(mlx_param.mlx_ptr)

    def __get_path_coords(
            self,
            enter: tuple[int, int],
            exit: tuple[int, int],
            directions: str | list[str]
    ) -> set[tuple[int, int]]:
        path_coords = set()
        if isinstance(directions, list):
            for direction in directions:
                path_coords.update(self.__get_path_coords(enter, exit, direction))
            return path_coords
        x, y = enter
        for step in directions:
            move_x, move_y = self.MOVEMENTS[step]
            x += move_x
            y += move_y
            current_pos = (x, y)
            if current_pos != enter and current_pos != exit:
                if current_pos not in path_coords:
                    path_coords.add(current_pos)
                else:
                    x -= move_x
                    y -= move_y
        return path_coords

    def __render_path_cells(self, long: set[tuple[int, int]], color: ColorCell):
        offset = int(self.CELL_SIZE * 0.15)
        inner_size = int(self.CELL_SIZE * 0.7)
        pixel_color = self.ALL_COLORS.get_color(color.value)
        for x, y in long:
            origin_x = (x * self.CELL_SIZE) + offset
            origin_y = (y * self.CELL_SIZE) + offset
            self.mlx.flat_canvas.draw_rectangle(
                origin_x,
                origin_y,
                inner_size,
                inner_size,
                pixel_color
            )

    def __drawway(self, long: set[tuple[int, int]]) -> None:
        self.__render_path_cells(long, ColorCell.WAY)

    def __undrawway(self, long: set[tuple[int, int]]) -> None:
        self.__render_path_cells(long, ColorCell.FLOOR)

    def visualizer(self) -> None:
        self.mlx = MlxPy()
        self.mlx.new_window(
            "Maze",
            self.WIDTH,
            self.HEIGHT,
            self.MARGIN
        )
        self.content = self.maze.solution
        self.__draw_maze()
        self.__drawway(self.__get_path_coords(
            self.maze.data.ENTRY,
            self.maze.data.EXIT,
            self.content
        ))
        self.mlx.load_window(self.__key_how, self.MARGIN)
