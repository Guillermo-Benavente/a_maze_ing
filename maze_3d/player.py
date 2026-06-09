from .data_3d import Data_3D
from .map import Map
from mlx_py import MlxPy
from maze import Cell
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
    """
    Parses active pressed keyboard buttons and maps them to delta directions.

    Args:
        keys (list[int]): Collection of raw active keycode entries.

    Returns:
        tuple[int, int]: Combined move and turn directions clamped to [-1, 1].
    """
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
    """
    Represents spatial position and orientation properties in continuous pixel
    space.
    """
    x: float
    """
    Absolute horizontal sub-pixel coordinate location on the layout canvas.
    """

    y: float
    """
    Absolute vertical sub-pixel coordinate location on the layout canvas.
    """

    rotation_angle: float
    """
    The current facing viewpoint orientation angle value, in radians.
    """


@dataclass
class MovementStats:
    radius: int = 3
    """
    The safety boundary thickness index assigned to prevent wall clipping.
    """

    move_speed: float = 2.5
    """
    Velocity displacement multiplier step size applied per frame update.
    """

    rotation_speed: float = 2.0 * (pi / 180)
    """
    Angular rotation scaling step size applied per frame update, in radians.
    """


class Player:
    """
    Tracks and updates the continuous camera entity representation.

    Manages input event hooks, handles trigonometric translation steps based on
    view angles, and isolates bounding wall collision thresholds usin
    localized grid testing.
    """
    transform: Transform
    stats: MovementStats
    settings: Data_3D
    map: Map

    def __init__(self, settings: Data_3D, map: Map) -> None:
        """
        Initializes the player transform context, centering the position
        precisely within the designated maze entry coordinate block.

        Args:
            settings (Data_3D): Shared configuration engine settings
                parameters context.
            map (Map): Matrix layout structure wrapper containing the core
                cell arrays.
        """
        self.settings = settings
        self.map = map
        start_x: float = (settings.data.ENTRY[0] + 0.5) * settings.CELS_SIZE
        start_y: float = (settings.data.ENTRY[1] + 0.5) * settings.CELS_SIZE
        start_angle: float = 45 * (pi / 180)
        self.transform = Transform(start_x, start_y, start_angle)
        self.stats = MovementStats()

    def _is_outside_bounds(self, x: float, y: float, radius: int) -> bool:
        """
        Verifies if target spatial coordinates breach the absolute outer
        boundaries of the global map canvas.

        Args:
            x (float): Horizontal pixel candidate coordinate to verify.
            y (float): Vertical pixel candidate coordinate to verify.
            radius (int): The hitbox boundary radius parameter.

        Returns:
            bool: True if tracking outside allowable layout limits, otherwise
                False.
        """
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
        """
        Evaluates active structural boundary parameters of a cell to detect
        internal hitbox profile overlap.

        Args:
            cell (Cell): Target grid cell structure to verify against.
            row (int): The vertical matrix grid tracking index of the cell.
            col (int): The horizontal matrix grid tracking index of the cell.
            x (float): Horizontal position coordinate candidate.
            y (float): Vertical position coordinate candidate.

        Returns:
            bool: True if candidate coordinates collide with active walls,
                otherwise False.
        """
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
        """
        Calculates localized bounding index scopes to optimize collision
        iterations.

        Args:
            target (float): Pixel focus coordinate candidate along a chosen
                vector axis.
            radius (int): The player hitbox radius value.
            max_limit (int): Maximum matrix grid limit boundary
                (width or height).

        Returns:
            tuple[int, int]: The minimum and maximum cell index bounds
                (start, end).
        """
        cell_size: int = self.settings.CELS_SIZE
        start: int = max(0, int((target - radius) // cell_size))
        end: int = min(max_limit - 1, int((target + radius) // cell_size))
        return (start, end)

    def is_colliding(self, target_x: float, target_y: float) -> bool:
        """
        Performs optimized grid-aligned collision testing around candidate
        coordinates.

        Args:
            target_x (float): Expected destination coordinate along the
                horizontal axis.
            target_y (float): Expected destination coordinate along the
                vertical axis.

        Returns:
            bool: True if moving into any wall object or outside bounds,
                otherwise False.
        """
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
        """
        Processes frame ticks, scaling rotation tracking, and executes
        independent axis movement translation sequences with strict wall
        collision avoidance rules.

        Args:
            keys (list[int]): Collection of raw active keycodes caught by
                window context hooks.
            param (MlxPy): Root graphical abstraction layer context parameter.
        """
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
