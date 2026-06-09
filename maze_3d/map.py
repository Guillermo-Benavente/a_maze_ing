from .data_3d import Data_3D
from maze import Cell


class Map():
    """
    Grid manager coordinate translator wrapping a 2D matrix structure of maze
    Cells.

    Provides critical boundary-checking interfaces and scales continuous
    sub-pixel coordinate floats into discrete matrix cell integers to query
    layout obstructions and walls during Raycasting visibility passes.
    """
    maze: list[list[Cell]]
    setings: Data_3D
    cell_size: int
    maze_width: int
    maze_height: int

    def __init__(self, maze: list[list[Cell]], setings: Data_3D) -> None:
        """
        Initializes the 3D-aligned map tracker instance.

        Args:
            maze (list[list[Cell]]): The core 2D list matrix layout
                representing the maze.
            setings (Data_3D): Shared configuration properties storing
                standard cell resolution rules.
        """
        self.maze = maze
        self.setings = setings
        self.cell_size = setings.CELS_SIZE
        self.maze_width = setings.data.WIDTH
        self.maze_height = setings.data.HEIGHT

    def get_cell(self, x: float, y: float) -> Cell | None:
        """
        Retrieves the structural Cell tracking instance situated at precise
            pixel coordinates.

        Args:
            x (float): Absolute horizontal sub-pixel coordinate position on
                the canvas.
            y (float): Absolute vertical sub-pixel coordinate position on the
                canvas.

        Returns:
            Cell | None: The intersecting grid cell object instance, or None
                if requested coordinates exceed absolute map boundaries.
        """
        coord_x = int(x // self.cell_size)
        coord_y = int(y // self.cell_size)
        if (
            coord_x < 0
            or coord_x >= self.maze_width
            or coord_y < 0
            or coord_y >= self.maze_height
        ):
            return None
        return self.maze[coord_y][coord_x]

    def get_position(self, x: float, y: float) -> tuple[int, int]:
        """
        Normalizes and compresses continuous canvas pixel dimensions into a
        standard integer map layout index tuple coordinate pair.

        Args:
            x (float): Continuous target location along the horizontal map
                axis.
            y (float): Continuous target location along the vertical map axis.

        Returns:
            tuple[int, int]: Mapped matrix array bounds (col_index, row_index).
        """
        coord_x = int(x // self.cell_size)
        coord_y = int(y // self.cell_size)
        return (coord_x, coord_y)

    def has_wall_at(self, x: float, y: float, direction: str) -> bool:
        """
        Queries an explicit cell index to determine whether a wall constraint
        is active along a designated cardinal edge.

        Out-of-bounds coordinate lookups are treated as active barriers by
        default to prevent camera leakage or clipping beyond layout
        constraints.

        Args:
            x (float): Continuous validation location on the horizontal map
                axis.
            y (float): Continuous validation location on the vertical map axis.
            direction (str): Single-character representation of the target
                heading cardinal wall ('N', 'S', 'E', or 'W').

        Returns:
            bool: True if a physical barrier obstacle exists or if lookup
                parameters leak beyond valid map bounds, otherwise False.
        """
        coord_x, coord_y = self.get_position(x, y)
        if (
            coord_x < 0
            or coord_x >= self.maze_width
            or coord_y < 0
            or coord_y >= self.maze_height
        ):
            return True
        cell = self.maze[coord_y][coord_x]
        if direction == "N":
            return cell.walls.north
        if direction == "S":
            return cell.walls.south
        if direction == "E":
            return cell.walls.east
        if direction == "W":
            return cell.walls.west
        return False
