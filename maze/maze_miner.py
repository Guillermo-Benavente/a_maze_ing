from typing import Callable
from random import choice, seed, randint, sample
from .maze_generator import MazeGenerator
from .cell import Cell
from .enums import CellType, LimitWallType


class MinerCell:
    cell: Cell
    is_dead: bool
    __slots__ = ('cell', 'is_dead')

    def __init__(self, cell: Cell) -> None:
        self.cell = cell
        self.is_dead = False


class MazeMiner():
    maze_generator: MazeGenerator
    DIRECTIONS: list[tuple[LimitWallType, int, int, LimitWallType]] = [
        (LimitWallType.NORTH, -1,  0, LimitWallType.SOUTH),
        (LimitWallType.EAST, 0,  1, LimitWallType.WEST),
        (LimitWallType.SOUTH, 1,  0, LimitWallType.NORTH),
        (LimitWallType.WEST, 0, -1, LimitWallType.EAST)
    ]

    def __init__(self, maze: MazeGenerator) -> None:
        self.maze_generator = maze
        seed(maze.data.SEED)
        self._mined()

    def _mined(self) -> None:
        required_direction: LimitWallType | None = None
        def imperfect_rule(new_cell: Cell, limit: LimitWallType, current_cell: Cell) -> bool:
            if CellType.FORTY_TWO in new_cell.cell_type:
                return False
            if required_direction is not None:
                return limit == required_direction
            return getattr(current_cell.walls, limit.name.lower())
        self.mined_cells: list[list[MinerCell]] = []
        width: int = self.maze_generator.data.WIDTH
        height: int = self.maze_generator.data.HEIGHT
        self.miner_map = [[None for _ in range(width)] for _ in range(height)]
        miners = int((width * height) * 0.04) or 1
        self.families: list[int] = list(range(miners))
        self._inital_points(miners)
        while self._has_cells_alive():
            self._maze_mining(miners)
        if not self.maze_generator.data.PERFECT:
            opposite = {
                LimitWallType.NORTH: LimitWallType.SOUTH,
                LimitWallType.SOUTH: LimitWallType.NORTH,
                LimitWallType.EAST: LimitWallType.WEST,
                LimitWallType.WEST: LimitWallType.EAST
            }
            for cell in self._get_dead_ends():
                open_wall = next(
                    wall_type for wall_type in LimitWallType 
                    if not getattr(cell.walls, wall_type.name.lower())
                )
                required_direction = opposite[open_wall]
                self._mined_cell(
                    self.maze_generator.maze, 
                    MinerCell(cell), 
                    imperfect_rule
                )
        del self.families
        del self.mined_cells
        del self.miner_map

    def _get_dead_ends(self) -> list[Cell]:
        dead_ends: list[Cell] = []
        for row in self.maze_generator.maze:
            for cell in row:
                if CellType.FORTY_TWO in cell.cell_type:
                    continue
                walls_count: int = sum([
                    cell.walls.north,
                    cell.walls.east,
                    cell.walls.south,
                    cell.walls.west
                ])
                if walls_count == 3:
                    dead_ends.append(cell)
        return dead_ends

    def _has_cells_alive(self) -> bool:
        for miner_list in self.mined_cells:
            for wrapper in miner_list:
                if not wrapper.is_dead:
                    return True
        return False

    def _inital_points(self, miners: int) -> None:
        valid_cells: list[Cell] = [
            cell
            for row in self.maze_generator.maze
            for cell in row
            if CellType.FORTY_TWO not in cell.cell_type
        ]
        initial_cells: list[Cell] = sample(valid_cells, miners)
        for miner, position_miner in enumerate(initial_cells):
            position_miner.zone_id = miner
            self.mined_cells.append([MinerCell(position_miner)])
            x, y = position_miner.position
            self.miner_map[y][x] = miner

    def _maze_mining(self, miners: int) -> None:
        def perfect_rule(new_cell: Cell, *_) -> bool:
            return self._try_cell_fusion(new_cell, miner)
        maze: list[list[Cell]] = self.maze_generator.maze
        for miner in range(miners):
            if not self.mined_cells[miner]:
                continue
            num_mined: int = randint(1, len(self.mined_cells[miner]))
            for _ in range(num_mined):
                cell_mined: MinerCell = choice(self.mined_cells[miner])
                if cell_mined.is_dead:
                    continue
                if not self._mined_cell(maze, cell_mined, perfect_rule):
                    cell_mined.is_dead = True

    def _mined_cell(
        self,
        maze: list[list[Cell]],
        cell_mined: MinerCell,
        can_mine_condition: Callable[[Cell, LimitWallType, Cell], bool]
    ):
        x: int
        y: int
        x, y = cell_mined.cell.position
        start_dir: int = randint(0, 3)
        step: int = 1 if randint(0, 1) == 0 else -1
        mined_successfully: bool = False
        for i in range(4):
            current_dir_index = (start_dir + (i * step)) % 4
            [
                limit,
                dy, dx,
                opposite_limit
            ] = self.DIRECTIONS[current_dir_index]

            if limit not in cell_mined.cell.limit_wall_type:
                new_cell: Cell = maze[y + dy][x + dx]
                if can_mine_condition(new_cell, limit, cell_mined.cell):
                    setattr(
                        cell_mined.cell.walls,
                        limit.name.lower(),
                        False
                    )
                    setattr(
                        new_cell.walls,
                        opposite_limit.name.lower(),
                        False
                    )
                    cell_mined.cell.encode_walls()
                    new_cell.encode_walls()
                    mined_successfully = True
                    break
        return mined_successfully

    def _try_cell_fusion(self, adjacent_cell: Cell, miner: int) -> bool:
        if CellType.FORTY_TWO in adjacent_cell.cell_type:
            return False
        x, y = adjacent_cell.position
        if self.miner_map[y][x] is None:
            self.miner_map[y][x] = miner
            adjacent_cell.zone_id = miner
            self.mined_cells[miner].append(MinerCell(adjacent_cell))
            return True
        else:
            leader_a = self._get_leader(miner)
            leader_b = self._get_leader(self.miner_map[y][x])
            if leader_a != leader_b:
                self.families[leader_b] = leader_a
                return True
        return False

    def _get_leader(self, m_id: int) -> int:
        if self.families[m_id] == m_id:
            return m_id
        self.families[m_id] = self._get_leader(self.families[m_id])
        return self.families[m_id]
