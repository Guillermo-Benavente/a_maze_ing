from random import choice, seed, randint, sample
from .maze_generator import MazeGenerator
from .cell import Cell
from .enums import CellType, LimitWallType


class MinerCell:
    """
    A minimal tracking wrapper that binds a grid Cell
    instance to an active/dead lifecycle state flag
    and marks cells currently engaged in border combat.
    """
    cell: Cell
    is_dead: bool
    in_battle: bool
    __slots__ = ('cell', 'is_dead', 'in_battle')

    def __init__(self, cell: Cell) -> None:
        """
        Initializes a tracking node wrapper for a cell,
        defining it as alive by default.

        Args:
            cell (Cell): The grid cell instance to track.
        """
        self.cell = cell
        self.is_dead = False
        self.in_battle = False


class MazeMiner():
    """
    Controls multi-agent parallel algorithm mining cycles
    to carve out valid paths inside the grid configuration.
    """
    maze_generator: MazeGenerator
    second_path_ensured: bool
    battle_space: set[tuple[tuple[int, int], tuple[int, int]]]
    battle_strikes: dict[tuple[tuple[int, int], tuple[int, int]], int]
    DIRECTIONS: list[tuple[LimitWallType, int, int, LimitWallType]] = [
        (LimitWallType.NORTH, -1,  0, LimitWallType.SOUTH),
        (LimitWallType.EAST, 0,  1, LimitWallType.WEST),
        (LimitWallType.SOUTH, 1,  0, LimitWallType.NORTH),
        (LimitWallType.WEST, 0, -1, LimitWallType.EAST)
    ]

    def __init__(self, maze: MazeGenerator) -> None:
        """
        Binds the source maze generator, seeds the global
        random generator, and initiates the mining execution.

        Args:
            maze (MazeGenerator): The main maze generator
                orchestrator instance.
        """
        self.maze_generator = maze
        seed(maze.data.SEED)
        self._mine()

    def _mine(self) -> None:
        """
        Executes the core mining loop: spawns miners at starting cells,
        runs iterative expansion cycles where each miner tries to carve
        a path into a neighboring cell, and then processes dead-end
        breaking and entry/exit neighbor cleanup for imperfect mazes.
        """
        miners: int
        self.mined_cells: list[list[MinerCell]] = []
        width: int = self.maze_generator.data.WIDTH
        height: int = self.maze_generator.data.HEIGHT
        if not self.maze_generator.data.PERFECT \
                and (width == 1 or height == 1):
            raise ValueError("Maze too small for imperfect mode")
        self.miner_map: list[list[int | None]] = [
            [None for _ in range(width)]
            for _ in range(height)
        ]
        self.second_path_ensured = False
        self.battle_space = set()
        self.battle_strikes = {}
        self.battle_blocked: set[tuple[int, int]] = set()
        self.is_small_maze: bool = width * height <= 4
        if not self.maze_generator.data.PERFECT:
            miners = max(2, int((width * height) * 0.04))
        else:
            miners = int((width * height) * 0.04) or 1
        self.families: list[int] = list(range(miners))
        self._init_miners(miners)
        while self._has_alive():
            self._mine_step(miners)
        if not self.maze_generator.data.PERFECT:
            all_dead_ends = self._get_dead_ends()
            open_rate: float = 0.4
            target_count: int = int(len(all_dead_ends) * open_rate)
            selected: list[Cell] = sample(all_dead_ends, target_count)
            for dead_end_cell in selected:
                try:
                    open_wall: LimitWallType = next(
                        wall_type for wall_type in LimitWallType
                        if not getattr(
                            dead_end_cell.walls, wall_type.name.lower()
                        )
                    )
                except StopIteration:
                    continue
                [
                    wall_to_break,
                    y_offset,
                    x_offset,
                    opposite_wall
                ] = next(
                    direction for direction in self.DIRECTIONS
                    if direction[3] == open_wall
                )
                if wall_to_break not in dead_end_cell.limit_wall_type:
                    cell_x, cell_y = dead_end_cell.position
                    target_y = cell_y + y_offset
                    target_x = cell_x + x_offset
                    if 0 <= target_y < height and 0 <= target_x < width:
                        adjacent = (
                            self.maze_generator.maze[target_y][target_x]
                        )
                        if CellType.FORTY_TWO not in adjacent.cell_type \
                           and (self.is_small_maze
                                or ((cell_y, cell_x)
                                    not in self.battle_blocked
                                    and (target_y, target_x)
                                    not in self.battle_blocked)):
                            setattr(
                                dead_end_cell.walls,
                                wall_to_break.name.lower(),
                                False
                            )
                            setattr(
                                adjacent.walls,
                                opposite_wall.name.lower(),
                                False
                            )
                            dead_end_cell.encode_walls()
                            adjacent.encode_walls()
            if width == 2 or height == 2:
                self._clear_entry_exit_neighbors()
        del self.battle_blocked
        del self.families
        del self.mined_cells
        del self.miner_map

    def _get_dead_ends(self) -> list[Cell]:
        """
        Scans the maze grid and returns all cells that have
        exactly three closed walls out of four. These are dead
        ends that can be broken open in imperfect mode to
        create additional paths and cycles.
        """
        dead_ends: list[Cell] = []
        for row in self.maze_generator.maze:
            for cell in row:
                if CellType.FORTY_TWO in cell.cell_type:
                    continue
                if CellType.LIMIT in cell.cell_type:
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

    def _clear_entry_exit_neighbors(self) -> None:
        """
        For 2-row or 2-column mazes, finds every cell adjacent
        to the entry and exit cells and opens all of their walls,
        ensuring entry and exit have multiple connections and
        the maze is truly imperfect.
        """
        maze: list[list[Cell]] = self.maze_generator.maze
        entry: Cell | None = None
        exit_: Cell | None = None
        for row in maze:
            for cell in row:
                if CellType.ENTRY in cell.cell_type:
                    entry = cell
                if CellType.EXIT in cell.cell_type:
                    exit_ = cell
        for focus in (entry, exit_):
            if focus is None:
                continue
            focus_col, focus_row = focus.position
            for _limit, _row_off, _col_off, _ in self.DIRECTIONS:
                if _limit in focus.limit_wall_type:
                    continue
                neighbor_row = focus_row + _row_off
                neighbor_col = focus_col + _col_off
                if not (0 <= neighbor_row < len(maze)
                        and 0 <= neighbor_col < len(maze[0])):
                    continue
                adjacent: Cell = maze[neighbor_row][neighbor_col]
                if CellType.FORTY_TWO in adjacent.cell_type:
                    continue
                adj_col, adj_row = adjacent.position
                for limit, row_off, col_off, opposite in self.DIRECTIONS:
                    if limit in adjacent.limit_wall_type:
                        continue
                    n_row = adj_row + row_off
                    n_col = adj_col + col_off
                    if not (0 <= n_row < len(maze)
                            and 0 <= n_col < len(maze[0])):
                        continue
                    neighbor: Cell = maze[n_row][n_col]
                    if CellType.FORTY_TWO in neighbor.cell_type:
                        continue
                    setattr(adjacent.walls, limit.name.lower(), False)
                    setattr(neighbor.walls, opposite.name.lower(), False)
                    adjacent.encode_walls()
                    neighbor.encode_walls()

    def _has_alive(self) -> bool:
        """
        Checks whether any miner agent in the tracking registry
        is still alive and able to expand further.

        Returns:
            bool: True if at least one tracked miner cell
                is still active, False otherwise.
        """
        for miner_list in self.mined_cells:
            for wrapper in miner_list:
                if not wrapper.is_dead:
                    return True
        return False

    def _init_miners(self, miners: int) -> None:
        """
        Distributes the initial miner agents across the grid.
        In perfect mode all start positions are fully random.
        In imperfect mode miners 0 and 1 are fixed at the Entry
        and Exit cells to guarantee a dual-path structure.

        Args:
            miners (int): Total number of miner agents to spawn.
        """
        valid_cells: list[Cell] = [
            cell
            for row in self.maze_generator.maze
            for cell in row
            if CellType.FORTY_TWO not in cell.cell_type
        ]

        if self.maze_generator.data.PERFECT:
            initial_cells = sample(valid_cells, miners)
        else:
            entry_cell: Cell = next(
                cell for cell in valid_cells
                if CellType.ENTRY in cell.cell_type
            )
            exit_cell: Cell = next(
                cell for cell in valid_cells
                if CellType.EXIT in cell.cell_type
            )
            remaining: list[Cell] = [
                cell for cell in valid_cells
                if cell is not entry_cell and cell is not exit_cell
            ]
            initial_cells = [entry_cell, exit_cell]
            if miners > 2:
                initial_cells.extend(sample(remaining, miners - 2))

        for miner, position_miner in enumerate(initial_cells):
            position_miner.zone_id = miner
            self.mined_cells.append([MinerCell(position_miner)])
            x, y = position_miner.position
            self.miner_map[y][x] = miner

    def _mine_step(self, miners: int) -> None:
        """
        Runs one iteration of mining: for each miner, picks a random
        number of living cells in its family and tries to expand each
        one into an unclaimed neighbor.

        Args:
            miners (int): Total number of miner agents.
        """
        maze: list[list[Cell]] = self.maze_generator.maze
        for miner in range(miners):
            if not self.mined_cells[miner]:
                continue
            living: list[MinerCell] = [
                wrapper for wrapper in self.mined_cells[miner]
                if not wrapper.is_dead
            ]
            if not living:
                continue
            num_mined: int = randint(1, len(living))
            for _ in range(num_mined):
                worker: MinerCell = choice(living)
                if worker.is_dead:
                    continue
                if not self._carve_cell(maze, worker, miner):
                    if not worker.in_battle:
                        worker.is_dead = True
                    worker.in_battle = False

    def _carve_cell(
            self,
            maze: list[list[Cell]],
            worker: MinerCell,
            miner: int,
    ) -> bool:
        """
        From a given miner cell, tries to carve into a random
        neighbor by removing the shared wall. Returns True if
        a wall was successfully broken, False otherwise.

        Args:
            maze (list[list[Cell]]): The full maze grid.
            worker (MinerCell): The miner cell to expand from.
            miner (int): The miner family identifier.

        Returns:
            bool: True if a wall was broken, False otherwise.
        """
        x, y = worker.cell.position
        start_dir: int = randint(0, 3)
        step: int = 1 if randint(0, 1) == 0 else -1
        mined_successfully: bool = False
        for i in range(4):
            current_dir_index = (start_dir + (i * step)) % 4
            [
                limit,
                row_off, col_off,
                opposite_limit
            ] = self.DIRECTIONS[current_dir_index]
            if limit not in worker.cell.limit_wall_type:
                neighbor_row: int = y + row_off
                neighbor_col: int = x + col_off
                if not (0 <= neighbor_row < len(maze)
                        and 0 <= neighbor_col < len(maze[0])):
                    continue
                new_cell: Cell = maze[neighbor_row][neighbor_col]
                if not getattr(worker.cell.walls, limit.name.lower()):
                    continue
                if self._try_fusion(worker, new_cell, miner):
                    setattr(
                        worker.cell.walls,
                        limit.name.lower(),
                        False
                    )
                    setattr(
                        new_cell.walls,
                        opposite_limit.name.lower(),
                        False
                    )
                    worker.cell.encode_walls()
                    new_cell.encode_walls()
                    mined_successfully = True
                    break
        return mined_successfully

    def _try_fusion(
            self,
            miner_cell: MinerCell,
            adjacent_cell: Cell,
            miner: int
    ) -> bool:
        """
        Attempts to absorb an unclaimed cell into the miner's
        family, or if the target cell belongs to a rival miner,
        initiates a battle to decide whether the wall stays or
        breaks open (imperfect mode) or merges the two families
        (perfect mode).

        Args:
            miner_cell (MinerCell): The cell initiating the dig.
            adjacent_cell (Cell): The target neighboring cell.
            miner (int): The miner family identifier.

        Returns:
            bool: True if the wall was broken, False otherwise.
        """
        if CellType.FORTY_TWO in adjacent_cell.cell_type:
            return False
        x, y = adjacent_cell.position
        if self.miner_map[y][x] is None:
            self.miner_map[y][x] = miner
            adjacent_cell.zone_id = miner
            self.mined_cells[miner].append(MinerCell(adjacent_cell))
            return True
        rival = self.miner_map[y][x]
        if rival == miner:
            return False
        leader_a = self._get_leader(miner)
        leader_b = self._get_leader(rival)
        if leader_a is None or leader_b is None:
            return False
        if leader_a != leader_b:
            if not self._battle_engagement(miner_cell, adjacent_cell):
                return False
            if not self.maze_generator.data.PERFECT:
                return True
            self.families[leader_b] = leader_a
            return True
        return False

    def _battle_engagement(
            self,
            miner_cell: MinerCell,
            adjacent_cell: Cell
    ) -> bool:
        """
        Manages the battle system between two rival miners
        contesting the same wall. After 10 strikes the wall
        is forced open. In imperfect mode the families stay
        separate (creating a loop). In perfect mode they merge.
        Also places a battle-blocked zone around the initiator
        to prevent adjacent battles from creating large rooms.
        """
        width: int = self.maze_generator.data.WIDTH
        height: int = self.maze_generator.data.HEIGHT
        wall_key: tuple[tuple[int, int], tuple[int, int]] = (
            min(miner_cell.cell.position, adjacent_cell.position),
            max(miner_cell.cell.position, adjacent_cell.position)
        )
        if wall_key in self.battle_space:
            hits = self.battle_strikes
            hits[wall_key] = hits.get(wall_key, 0) + 1
            miner_cell.in_battle = True
            if hits[wall_key] >= 10:
                self.battle_space.discard(wall_key)
                del hits[wall_key]
                return True
            return False
        if not self.maze_generator.data.PERFECT:
            if not self.is_small_maze:
                cell_col, cell_row = miner_cell.cell.position
                if (cell_row, cell_col) in self.battle_blocked:
                    return False
                neighbor_offsets: list[tuple[int, int]]
                if width <= 3 and height <= 3:
                    neighbor_offsets = [
                        (-1, 0), (1, 0), (0, -1), (0, 1)
                    ]
                else:
                    neighbor_offsets = [
                        (-1, -1), (-1, 0), (-1, 1),
                        (0, -1), (0, 1),
                        (1, -1), (1, 0), (1, 1)
                    ]
                for row_off, col_off in neighbor_offsets:
                    n_row, n_col = cell_row + row_off, cell_col + col_off
                    if 0 <= n_row < height and 0 <= n_col < width:
                        self.battle_blocked.add((n_row, n_col))
            self.battle_space.add(wall_key)
            self.battle_strikes[wall_key] = 1
            miner_cell.in_battle = True
            return False
        self.battle_space.add(wall_key)
        return True

    def _get_leader(self, m_id: int | None) -> int | None:
        """
        Recursive union-find path compression lookup.
        Traverses the families array to find the absolute
        root zone identifier for a given miner.

        Args:
            m_id (int | None): The miner identifier to look up.

        Returns:
            int | None: The root zone ID, or None for a
                None input.
        """
        if m_id is None:
            return None
        if self.families[m_id] == m_id:
            return m_id
        leader: int | None = self._get_leader(self.families[m_id])
        if leader is None:
            return None
        self.families[m_id] = leader
        return self.families[m_id]
