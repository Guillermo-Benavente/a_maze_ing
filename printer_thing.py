from maze_3d.player import Player
from sys import argv
from maze_3d.raycaster import Raycaster
from functools import partial
from time import sleep
from collections import deque
from mlx import Mlx  # type: ignore
from mlx_py import MlxPy, FlatCanvas
from maze.cell import Cell
from maze.enums import CellType
from colors import AllColors, ColorCell
from parser_config import lector, Data
from maze.maze_generator import MazeGenerator
import os
from pydantic import ValidationError
from buttons import Buttons as but


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
        self.new_data = None
        ancho = int(os.environ.get("SCREEN_WIDTH", 1920))
        alto = int(os.environ.get("SCREEN_HEIGHT", 1080))
        self.__optimize_size(maze, ancho, alto)
        self.WIDTH = maze.data.WIDTH * self.CELL_SIZE
        self.HEIGHT = maze.data.HEIGHT * self.CELL_SIZE
        self.MENU = [
            "1 - Change all Colors",
            "2 - Change wall Colors",
            "3 - Change enter Colors",
            "4 - Change way Colors",
            "5 - Change exit Colors",
            "6 - Change cells Colors",
            "7 - Change 42 Colors",
            "8 - New",
            "9 - Animation",
            "0 - All ways",
            "ESC - Exit"
            ]
        self.MAINMENU_HEIGHT = 20 + 20 * (len(self.MENU)//2 + 2)
        self.MAINMENU_WIDTH = 0
        for i in range(0, len(self.MENU), 2):
            num = 30 + len(self.MENU[i]) * 10
            if self.MENU[-1] != self.MENU[i]:
                num += len(self.MENU[i + 1]) * 10 + 48
            if num > (self.WIDTH + self.MAINMENU_WIDTH):
                self.MAINMENU_WIDTH = num - self.WIDTH

    def __optimize_size(
            self,
            maze: MazeGenerator,
            tkwidth: int,
            tkheight: int,
            size: int = 3
    ) -> None:
        width = maze.data.WIDTH * size
        height = maze.data.HEIGHT * size
        if tkheight > height and tkwidth > width:
            self.__optimize_size(maze, tkwidth, tkheight, size + 1)
        elif (tkheight < height or tkwidth < width) and size != 3:
            self.CELL_SIZE = size - 1
            x = round(self.CELL_SIZE * 0.04) or 1
            self.WALL_THICKNESS = x
        else:
            self.CELL_SIZE = size
            x = round(self.CELL_SIZE * 0.04) or 1
            self.WALL_THICKNESS = x

    def __get_cell_color(
            self,
            cell: Cell,
            is_wall: bool = False
    ) -> tuple[int, int, int, int]:
        if CellType.FORTY_TWO in cell.cell_type:
            return self.ALL_COLORS.get_color(
                ColorCell.WALL_42.value
                if is_wall
                else ColorCell.FLOOR_42.value
            )
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

    def __menu(self, param: Mlx) -> None:
        _ = param.mlx_ptr
        self.mlx.mlx_put_image_to_window(self.MARGIN, self.MAINMENU_WIDTH)
        self.mlx.mlx_do_sync()
        for i in range(0, len(self.MENU), 2):
            y_pos = self.HEIGHT + 30 + (i // 2) * 20
            self.mlx.mlx_string_put(30, y_pos, 0xFFFFFF, self.MENU[i])
            if self.MENU[-1] != self.MENU[i]:
                self.mlx.mlx_string_put(
                    (self.WIDTH + self.MAINMENU_WIDTH) // 2,
                    y_pos,
                    0xFFFFFF,
                    self.MENU[i + 1]
                )
        self.mlx.mlx_do_sync()

    def __key_how(self, key: int, mlx_param: Mlx) -> None:
        if key in (but.BUTTON_1.value,
                   but.BUTTON_2.value,
                   but.BUTTON_3.value,
                   but.BUTTON_4.value,
                   but.BUTTON_5.value,
                   but.BUTTON_6.value,
                   but.BUTTON_7.value,
                   but.BUTTON_8.value,
                   but.BUTTON_9.value,
                   but.BUTTON_0.value
                   ):
            if key == but.BUTTON_1.value:
                self.ALL_COLORS.all_colors()
            if key == but.BUTTON_2.value:
                self.ALL_COLORS.evol_color(ColorCell.WALL.value)
            if key == but.BUTTON_3.value:
                self.ALL_COLORS.evol_color(ColorCell.ENTRY.value)
            if key == but.BUTTON_4.value:
                self.ALL_COLORS.evol_color(ColorCell.WAY.value)
            if key == but.BUTTON_5.value:
                self.ALL_COLORS.evol_color(ColorCell.EXIT.value)
            if key == but.BUTTON_6.value:
                self.ALL_COLORS.evol_color(ColorCell.FLOOR.value)
            if key == but.BUTTON_7.value:
                self.ALL_COLORS.evol_color(ColorCell.FLOOR_42.value)
            if key == but.BUTTON_8.value:
                try:
                    data = Data.model_validate(lector(argv[1]))
                    if (
                        data.SEED != self.maze.data.SEED or
                        data.ENTRY != self.maze.data.ENTRY or
                        data.EXIT != self.maze.data.EXIT or
                        data.WIDTH != self.maze.data.WIDTH or
                        data.HEIGHT != self.maze.data.HEIGHT or
                        data.PERFECT != self.maze.data.PERFECT
                       ):
                        self.new_data = data
                        self.mlx.close_window()
                        self.mlx.mlx_loop_exit()
                except (ValidationError,
                        ValueError,
                        AssertionError,
                        PermissionError
                        ) as e:
                    if isinstance(e, ValidationError):
                        for error in e.errors():
                            print(error["msg"])
                    else:
                        print(e)
                except Exception as e:
                    print(e)
                return
            if key == but.BUTTON_9.value:
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
            if key == but.BUTTON_0.value:
                deque(self.maze.algoritm["algoritm"](), maxlen=0)
                all_ways: set[tuple[int, int]] = set()
                for i in self.maze.algoritm["list"]():
                    all_ways.update(self.__get_path_coords(
                            self.maze.data.ENTRY,
                            self.maze.data.EXIT,
                            i
                    ))
                self.content = self.maze.algoritm["list"]()
            self.__draw_maze()
            self.__drawway(self.__get_path_coords(
                self.maze.data.ENTRY,
                self.maze.data.EXIT,
                self.content
            ))
            self.mlx.mlx_put_image_to_window(self.MARGIN)
            self.mlx.mlx_do_sync()
        if key == but.BUTTON_SCAPE.value:
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
                path_coords.update(
                    self.__get_path_coords(enter, exit, direction)
                )
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

    def __render_path_cells(
            self,
            long: set[tuple[int, int]],
            color: ColorCell
    ) -> None:
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

    def visualizer(self, mlx: MlxPy | None = None) -> None:
        if not mlx:
            self.mlx = MlxPy()
        else:
            self.mlx = mlx
        self.mlx.new_window(
            "Maze",
            self.WIDTH,
            self.HEIGHT,
            self.MAINMENU_WIDTH,
            self.MAINMENU_HEIGHT,
            self.MARGIN
        )
        self.content = self.maze.solution
        self.__draw_maze()
        self.__drawway(self.__get_path_coords(
            self.maze.data.ENTRY,
            self.maze.data.EXIT,
            self.content
        ))
        self.mlx.load_window(
            self.__key_how,
            self.__menu, self.MARGIN,
            self.MAINMENU_WIDTH
        )

        self.mlx.close_window()

    def found_exit(self, player: Player) -> bool:
        pos = player.transform
        cell = player.map.get_cell(pos.x, pos.y)
        if isinstance(cell, Cell):
            return CellType.EXIT in cell.cell_type
        return False

    def __maze3D(self, player: Player, map: Raycaster, param: Mlx) -> int:
        teclas = self.mlx.key_pressed()
        pos = player.transform
        if (but.BUTTON_SCAPE.value in teclas or self.found_exit(player)):
            self.mlx.close_window()
            param.mlx_loop_exit(param.mlx_ptr)
            return 0
        player.update(teclas, param)
        map.cast_all_rays()
        map.render(self.mlx)
        print("\033[H\033[2J", end="")
        self.mlx.mlx_put_image_to_window(self.MARGIN)
        self.maze.view_maze_ascii(player.map.get_position(pos.x, pos.y))
        return 0

    def visualizer_3d(self, player: Player, map: Raycaster) -> None:
        self.mlx = MlxPy()
        self.mlx.new_window(
            "3D",
            map.map.setings.WINDOW_WIDTH,
            map.map.setings.WINDOW_HEIGHT,
            0,
            0,
            10
        )
        log = partial(self.__maze3D, player, map)
        self.mlx.load_window_3d(log)
