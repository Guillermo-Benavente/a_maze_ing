from sys import argv, maxsize as maxs
from time import sleep
from collections import deque
from mlx import Mlx
from mlx_py import MlxPy, FlatCanvas
from maze.cell import Cell
from maze.enums import CellType
from colors import AllColors, ColorCell
from parser_config import lector, Data
from maze.maze_generator import MazeGenerator
import os

class Drawer():
    WIDTH: int
    HEIGHT: int
    WALL_THICKNESS: int
    ALL_COLORS = AllColors()
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
        ancho = int(os.environ.get("SCREEN_WIDTH", 1920))
        alto = int(os.environ.get("SCREEN_HEIGHT", 1080))
        self.__optimize_size(maze, ancho, alto)
        self.WIDTH = maze.data.WIDTH * self.CELL_SIZE
        self.HEIGHT = maze.data.HEIGHT * self.CELL_SIZE

    def __optimize_size(self, maze: MazeGenerator, tkwidth: int, tkheight: int,  size: int = 3) -> None:
        width = maze.data.WIDTH * size
        height = maze.data.HEIGHT * size
        if tkheight > height and tkwidth > width:
            self.__optimize_size(maze, tkwidth, tkheight, size + 1)
        elif tkheight < height or tkwidth < width:
            self.CELL_SIZE = size - 1
            x = round(self.CELL_SIZE * 0.04) or 1
            self.WALL_THICKNESS = x
        else:
            self.CELL_SIZE = size
            x = round(self.CELL_SIZE * 0.04) or 1
            self.WALL_THICKNESS = x

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
                    canvas.draw_rectangle(
                        origin_x,
                        origin_y,
                        self.CELL_SIZE,
                        self.WALL_THICKNESS,
                        wall_color
                    )
                if cell.walls.west:
                    canvas.draw_rectangle(
                        origin_x,
                        origin_y,
                        self.WALL_THICKNESS,
                        self.CELL_SIZE,
                        wall_color
                    )
                if cell.walls.south:
                    canvas.draw_rectangle(
                        origin_x,
                        origin_y + self.CELL_SIZE - self.WALL_THICKNESS,
                        self.CELL_SIZE,
                        self.WALL_THICKNESS,
                        wall_color
                    )
                if cell.walls.east:
                    canvas.draw_rectangle(
                        origin_x + self.CELL_SIZE - self.WALL_THICKNESS,
                        origin_y,
                        self.WALL_THICKNESS,
                        self.CELL_SIZE,
                        wall_color
                    )

    def __key_how(self, key: int, mlx_param: Mlx) -> None:
        if key in (49, 50, 51, 52, 53):
            if key == 49:
                self.ALL_COLORS.all_colors()
            elif key == 50:
                self.mlx.close_window()
                mlx_param.mlx_loop_exit(mlx_param.mlx_ptr)
                data = Data.model_validate(lector(argv[1]))
                maze: MazeGenerator = MazeGenerator(data)
                draw = Drawer(maze)
                draw.visualizer()
                return
            elif key == 51:
                self.__draw_maze()
                for algorithm_step in self.maze.algoritm["algoritm"]():
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
                deque(self.maze.algoritm["algoritm"](), maxlen=0)
                if len(self.maze.algoritm["list"]()) != 0:
                    self.solution = self.maze.algoritm["sorter"]()
            self.__draw_maze()
            self.__drawway(self.__get_path_coords(
                self.maze.data.ENTRY,
                self.maze.data.EXIT,
                self.content
            ))
            self.mlx.mlx_put_image_to_window(self.MARGIN)
        if key == 65307:
            self.mlx.close_window()
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
