from typing import TextIO
from sys import stdout, stderr
from parser_config import Data
from .enums import CellType, LimitWallType
from .cell import Cell


class MazeGenerator():
    maze: list[list[Cell]]
    data: Data

    def __init__(self, data: Data) -> None:
        from .maze_miner import MazeMiner
        self.maze = [
            [
                Cell((width, height))
                for width in range(data.WIDTH)
            ]
            for height in range(data.HEIGHT)
        ]
        self.data = data
        self._create_maze()
        MazeMiner(self)
        self.algoritm = self.data.ALGORITM(self.maze)
        for i in self.algoritm["algoritm"]():
            pass
        if len(self.algoritm["list"]()) != 0:
            self.solution = self.algoritm["sorter"]()
        else:
            self.solution = None
        self._generatedoc()

    def _generatedoc(self) -> None:
        with open(self.data.OUTPUT_FILE, "w") as fd:
            for i in self.maze:
                for j in i:
                    print(j.hexadecimal, end="", file=fd)
                print("", file=fd)
            entry = f"{self.data.ENTRY}".strip('(').strip(')')
            exits = f"{self.data.EXIT}".strip('(').strip(')')
            print(f"\n{entry.replace(' ', '')}", file=fd)
            print(exits.replace(' ', ''), file=fd)
            print(self.solution, file=fd)

    def _create_maze(self) -> None:
        start_height: int = 0
        start_width: int = 0
        if self.data.WIDTH <= 7 and self.data.HEIGHT <= 5:
            print("Maze too small to draw '42' pattern.", file=stderr)
        elif self.data.WIDTH <= 7 or self.data.HEIGHT <= 5:
            if self.data.WIDTH <= 7:
                print(
                    "Width maze too small to draw '42' pattern.",
                    file=stderr
                )
            if self.data.HEIGHT <= 5:
                print(
                    "height maze too small to draw '42' pattern.",
                    file=stderr
                )
        else:
            if self.data.WIDTH != 8:
                start_width = (self.data.WIDTH // 2) - 3
            if self.data.HEIGHT != 6:
                start_height = (self.data.HEIGHT // 2) - 2
        self._search_inout()
        self._create_limits()
        self._create_forty_two(start_height, start_width)

    def _create_forty_two(
        self,
        start_height: int,
        start_width: int
    ) -> None:
        if self.data.WIDTH <= 7 or self.data.HEIGHT <= 5:
            return
        for y in range(5):
            for x in range(7):
                height = start_height + y
                width = start_width + x
                cell = self.maze[height][width]
                if (
                    x != 3 and
                    not (y == 0 and (x == 1 or x == 2)) and
                    not (y == 1 and 1 <= x <= 5) and
                    not (y == 3 and x in [0, 1, 5, 6]) and
                    not (y == 4 and (x == 0 or x == 1))
                ):
                    if (
                        CellType.ENTRY in cell.cell_type or
                        CellType.EXIT in cell.cell_type
                    ):
                        raise Exception(
                            (
                                "Entry or exit coordinates"
                                " collide with the '42' pattern zone."
                            )
                        )
                    cell.cell_type.append(CellType.FORTY_TWO)

    def _create_limits(self) -> None:
        height: int = self.data.HEIGHT
        width: int = self.data.WIDTH

        for x in range(width):
            north: Cell = self.maze[0][x]
            south: Cell = self.maze[height - 1][x]
            north.cell_type.append(CellType.LIMIT)
            north.limit_wall_type.append(LimitWallType.NORTH)
            south.cell_type.append(CellType.LIMIT)
            south.limit_wall_type.append(LimitWallType.SOUTH)
        for y in range(height):
            west: Cell = self.maze[y][0]
            east: Cell = self.maze[y][width - 1]
            west.cell_type.append(CellType.LIMIT)
            west.limit_wall_type.append(LimitWallType.WEST)
            east.cell_type.append(CellType.LIMIT)
            east.limit_wall_type.append(LimitWallType.EAST)

    def _search_inout(self) -> None:
        x_entry: int
        y_entry: int
        x_exit: int
        y_exit: int
        x_entry, y_entry = self.data.ENTRY
        x_exit, y_exit = self.data.EXIT
        self.maze[y_entry][x_entry].cell_type.append(CellType.ENTRY)
        self.maze[y_exit][x_exit].cell_type.append(CellType.EXIT)

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
