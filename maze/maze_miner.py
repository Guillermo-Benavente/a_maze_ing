from random import choice, seed, randint, sample
from .maze_generator import MazeGenerator
from .cell import Cell
from .enums import CellType, LimitWallType


class MazeMiner():
    maze_generator: MazeGenerator

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze_generator = maze
        seed(maze.data.SEED)
        self._mined()

    def _mined(self) -> None:
        self.valid_cells: set[Cell] = self.maze_generator.valid_cells
        self.mined_cells: list[list[Cell]] = []
        miners: int = 1
        if (
            self.maze_generator.data.WIDTH >= 5 and
            self.maze_generator.data.HEIGHT >= 5
        ):
            miners = int(
                (
                    self.maze_generator.data.WIDTH *
                    self.maze_generator.data.HEIGHT
                ) * 0.04
            )
        self.families: list[int] = list(range(miners))
        self._inital_points(miners)
        while self.valid_cells:
            self._maze_mining(miners)
        del self.families
        del self.mined_cells
        del self.valid_cells

    def _inital_points(self, miners: int) -> None:
        for miner in range(miners):
            position_miner: Cell = sample(
                sorted(self.valid_cells, key=lambda c: c.position), 1
            )[0]
            position_miner.miner_id = miner
            self.mined_cells.append([position_miner])
            self.valid_cells.remove(position_miner)

    def _maze_mining(self, miners: int) -> None:
        maze: list[list[Cell]] = self.maze_generator.maze
        for miner in range(miners):
            num_mined: int = randint(1, len(self.mined_cells[miner]))
            for _ in range(num_mined):
                cell_mined: Cell = choice(self.mined_cells[miner])
                [x, y] = cell_mined.position
                openings: int = randint(0, 15)
                new_cell: Cell | None = None
                if (
                    LimitWallType.NORTH
                    not in cell_mined.limit_wall_type and
                    openings & 8
                ):
                    new_cell = maze[y - 1][x]
                    if self._try_cell_fusion(new_cell, miner):
                        cell_mined.walls.north = False
                        new_cell.walls.south = False
                if (
                    LimitWallType.EAST
                    not in cell_mined.limit_wall_type and
                    openings & 4
                ):
                    new_cell = maze[y][x + 1]
                    if self._try_cell_fusion(new_cell, miner):
                        cell_mined.walls.east = False
                        new_cell.walls.west = False
                if (
                    LimitWallType.SOUTH
                    not in cell_mined.limit_wall_type and
                    openings & 2
                ):
                    new_cell = maze[y + 1][x]
                    if self._try_cell_fusion(new_cell, miner):
                        cell_mined.walls.south = False
                        new_cell.walls.north = False
                if (
                    LimitWallType.WEST
                    not in cell_mined.limit_wall_type and
                    openings & 1
                ):
                    new_cell = maze[y][x - 1]
                    if self._try_cell_fusion(new_cell, miner):
                        cell_mined.walls.west = False
                        new_cell.walls.east = False
                if new_cell:
                    cell_mined.encode_walls()
                    new_cell.encode_walls()

    def _try_cell_fusion(self, adjacent_cell: Cell, miner: int) -> bool:
        if CellType.FORTY_TWO not in adjacent_cell.cell_type:
            if adjacent_cell in self.valid_cells:
                adjacent_cell.miner_id = miner
                self.mined_cells[miner].append(adjacent_cell)
                self.valid_cells.remove(adjacent_cell)
                return True
            elif adjacent_cell.miner_id is not None:
                leader_a = self._get_leader(miner)
                leader_b = self._get_leader(adjacent_cell.miner_id)
                if leader_a != leader_b:
                    self.families[leader_b] = leader_a
                    return True
        return False

    def _get_leader(self, m_id: int) -> int:
        if self.families[m_id] == m_id:
            return m_id
        self.families[m_id] = self._get_leader(self.families[m_id])
        return self.families[m_id]
