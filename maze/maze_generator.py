from typing import TextIO
from sys import stdout, stderr
from parser_config import Data
from .enums import CellType, LimitWallType
from .cell import Cell


class MazeGenerator():
    maze: list[list[Cell]]
    valid_cells: set[Cell]
    data: Data

    def __init__(self, data: Data) -> None:
        from .maze_miner import MazeMiner
        self.maze = []
        self.valid_cells = set()
        self.data = data
        self._create_maze()
        MazeMiner(self)

    def _create_maze(self) -> None:
        start_height: int = 0
        start_width: int = 0
        if self.data.WIDTH <= 7 and self.data.HEIGHT <= 5:
            print("Maze too small to draw '42' pattern.", file=stderr)
        elif self.data.WIDTH <= 7 or self.data.HEIGHT <= 5:
            if self.data.WIDTH <= 7:
                print("Width maze too small to draw '42' pattern.", file=stderr)
            if self.data.HEIGHT <= 5:
                print("height maze too small to draw '42' pattern.", file=stderr)
        else:
            if self.data.WIDTH != 8:
                start_width = (self.data.WIDTH // 2) - 3
            if self.data.HEIGHT != 6:
                start_height = (self.data.HEIGHT // 2) - 2
        for height in range(self.data.HEIGHT):
            cells: list[Cell] = []
            for width in range(self.data.WIDTH):
                cell: Cell = Cell((width, height))
                self._search_inout(cell)
                self._create_limits(cell)
                if self.data.WIDTH > 7 and self.data.HEIGHT > 5:
                    self._create_forty_two(
                        cell,
                        start_height,
                        start_width
                    )
                if CellType.FORTY_TWO not in cell.cell_type:
                    self.valid_cells.add(cell)
                cells.append(cell)
            self.maze.append(cells)

    def _create_forty_two(
        self,
        cell: Cell,
        start_height: int,
        start_width: int
    ) -> None:
        height: int = cell.position[1]
        width: int = cell.position[0]
        if (
            start_height <= height < start_height + 5 and
            start_width <= width < start_width + 7
        ):
            i: int = height - start_height
            j: int = width - start_width
            if (
                    j != 3 and
                    not (i == 0 and (j == 1 or j == 2)) and
                    not (i == 1 and 1 <= j <= 5) and
                    not (i == 3 and j in [0, 1, 5, 6]) and
                    not (i == 4 and (j == 0 or j == 1))
            ):
                if (
                    CellType.ENTRY in cell.cell_type or
                    CellType.EXIT in cell.cell_type
                ):
                    raise Exception("Entry or exit coordinates collide with the '42' pattern zone.")
                else:
                    cell.cell_type.append(CellType.FORTY_TWO)

    def _create_limits(self, cell: Cell) -> None:
        height: int = cell.position[1]
        width: int = cell.position[0]
        if (
            height == 0 or
            width == 0 or
            height == self.data.HEIGHT - 1 or
            width == self.data.WIDTH - 1
        ):
            cell.cell_type.append(CellType.LIMIT)
            if height == 0:
                cell.limit_wall_type.append(LimitWallType.NORTH)
            if width == 0:
                cell.limit_wall_type.append(LimitWallType.WEST)
            if height == self.data.HEIGHT - 1:
                cell.limit_wall_type.append(LimitWallType.SOUTH)
            if width == self.data.WIDTH - 1:
                cell.limit_wall_type.append(LimitWallType.EAST)

    def _search_inout(self, cell: Cell) -> None:
        height: int = cell.position[1]
        width: int = cell.position[0]
        if (
            self.data.ENTRY[0] == width and
            self.data.ENTRY[1] == height
        ):
            cell.cell_type.append(CellType.ENTRY)
        elif (
            self.data.EXIT[0] == width and
            self.data.EXIT[1] == height
        ):
            cell.cell_type.append(CellType.EXIT)

    def view_maze(self) -> None:
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                print(self.maze[height][width].hexadecimal, end="")
            print()

    def view_maze_ascii(self, file: TextIO = stdout) -> None:
        WALL_H: str = "---"
        WALL_V: str = "|"
        CORNER: str = "+"
        EMPTY_H: str = "   "
        EMPTY_V: str = " "

        for height in range(self.data.HEIGHT):
            line_top = ""
            line_mid = ""
            for width in range(self.data.WIDTH):
                cell = self.maze[height][width]
                n = bool(cell.binary & 8)
                w = bool(cell.binary & 1)
                if CellType.FORTY_TWO in cell.cell_type:
                    line_top += "####"
                    line_mid += "####"
                else:
                    line_top += CORNER + (WALL_H if n else EMPTY_H)
                    char_w = WALL_V if w else EMPTY_V
                    if CellType.ENTRY in cell.cell_type:
                        content = "[_]"
                    elif CellType.EXIT in cell.cell_type:
                        content = "_H_"
                    else:
                        content = "   "
                    line_mid += char_w + content
            last_cell = self.maze[height][-1]
            e = bool(last_cell.binary & 4)
            line_top += CORNER
            line_mid += (WALL_V if e else EMPTY_V)
            print(line_top, file=file)
            print(line_mid, file=file)
        last_row_line = ""
        for width in range(self.data.WIDTH):
            cell = self.maze[self.data.HEIGHT - 1][width]
            s = bool(cell.binary & 2)
            last_row_line += CORNER + (WALL_H if s else EMPTY_H)
        print(last_row_line + CORNER, file=file)
