from .data_3d import Data_3D
from .map import Map
from mlx_py import MlxPy
from maze.cell import Cell
from dataclasses import dataclass
from buttons import Buttons as btn
from math import sin, cos, pi


INPUT_MAPPING = {
    # NORTH
    btn.BUTTON_UP.value: (1, 0),
    btn.BUTTON_W.value: (1, 0),
    btn.BUTTON_NUMPATH_8.value: (1, 0),
    # SOUTH
    btn.BUTTON_DOWN.value: (-1, 0),
    btn.BUTTON_S.value: (-1, 0),
    btn.BUTTON_NUMPATH_2.value: (-1, 0),
    # EAST
    btn.BUTTON_RIGHT.value: (0, 1),
    btn.BUTTON_D.value: (0, 1),
    btn.BUTTON_NUMPATH_6.value: (0, 1),
    # WEST
    btn.BUTTON_LEFT.value: (0, -1),
    btn.BUTTON_A.value: (0, -1),
    btn.BUTTON_NUMPATH_4.value: (0, -1)
}


def handle_player_input(keys: list[int]) -> tuple[int, int]:
    walk_direction = 0
    turn_direction = 0
    for key in keys:
        if key in INPUT_MAPPING:
            walk, turn = INPUT_MAPPING[key]
            walk_direction += walk
            turn_direction += turn
    return (max(-1, min(1, walk_direction)), max(-1, min(1, turn_direction)))


@dataclass
class Transform:
    x: float
    y: float
    rotation_angle: float


@dataclass
class MovementStats:
    radius: int = 3
    move_speed: float = 2.5
    rotation_speed: float = 2.0 * (pi / 180)


class Player:
    transform: Transform
    stats: MovementStats
    settings: Data_3D
    map: Map

    def __init__(self, settings: Data_3D, map: Map) -> None:
        self.settings = settings
        self.map = map
        start_x: float = (settings.data.ENTRY[0] + 0.5) * settings.CELS_SIZE
        start_y: float = (settings.data.ENTRY[1] + 0.5) * settings.CELS_SIZE
        start_angle: float = 45 * (pi / 180)
        self.transform = Transform(start_x, start_y, start_angle)
        self.stats = MovementStats()

    def _is_outside_bounds(self, x: float, y: float, radius: int) -> bool:
        cell_size: int = self.settings.CELS_SIZE
        max_x: int = self.settings.data.WIDTH * cell_size
        max_y: int = self.settings.data.HEIGHT * cell_size
        return (
            x < radius
            or x >= max_x - radius
            or y < radius
            or y >= max_y - radius
        )

    def _hits_cell_wall(
        self,
        cell: Cell,
        row: int,
        col: int,
        x: float,
        y: float
    ) -> bool:
        cell_size: int = self.settings.CELS_SIZE
        radius: int = self.stats.radius
        if cell.walls.east and x + radius > (col + 1) * cell_size:
            return True
        if cell.walls.west and x - radius < col * cell_size:
            return True
        if cell.walls.south and y + radius > (row + 1) * cell_size:
            return True
        if cell.walls.north and y - radius < row * cell_size:
            return True
        return False

    def _get_cell_range(
        self,
        target: float,
        radius: int,
        max_limit: int
    ) -> tuple[int, int]:
        cell_size: int = self.settings.CELS_SIZE
        start: int = max(0, int((target - radius) // cell_size))
        end: int = min(max_limit - 1, int((target + radius) // cell_size))
        return (start, end)

    def is_colliding(self, target_x: float, target_y: float) -> bool:
        radius: int = self.stats.radius
        width: int = self.settings.data.WIDTH
        height: int = self.settings.data.HEIGHT
        if self._is_outside_bounds(target_x, target_y, radius):
            return True
        start_col, end_col = self._get_cell_range(target_x, radius, width)
        start_row, end_row = self._get_cell_range(target_y, radius, height)
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell: Cell = self.map.maze[row][col]
                if self._hits_cell_wall(cell, row, col, target_x, target_y):
                    return True
        return False

    def update(self, keys: list[int], param: MlxPy) -> None:
        _ = param
        walk_direction, turn_direction = handle_player_input(keys)
        self.transform.rotation_angle += (
            turn_direction * self.stats.rotation_speed
        )
        self.transform.rotation_angle %= 2.0 * pi
        move_step = walk_direction * self.stats.move_speed
        move_x = cos(self.transform.rotation_angle) * move_step
        move_y = sin(self.transform.rotation_angle) * move_step
        if (
            move_x != 0
            and not self.is_colliding(
                self.transform.x + move_x,
                self.transform.y
            )
        ):
            self.transform.x += move_x
        if (
            move_y != 0
            and not self.is_colliding(
                self.transform.x,
                self.transform.y + move_y
            )
        ):
            self.transform.y += move_y
