from .data_3d import Data_3D
from maze.cell import Cell


class Map():
    maze: list[list[Cell]]
    setings: Data_3D
    cell_size: int
    maze_width: int
    maze_height: int

    def __init__(self, maze: list[list[Cell]], setings: Data_3D) -> None:
        self.maze = maze
        self.setings = setings
        self.cell_size = setings.CELS_SIZE
        self.maze_width = setings.data.WIDTH
        self.maze_height = setings.data.HEIGHT

    def get_cell(self, x: float, y: float) -> Cell | None:
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
        coord_x = int(x // self.cell_size)
        coord_y = int(y // self.cell_size)
        return (coord_x, coord_y)

    def has_wall_at(self, x: float, y: float, direction: str) -> bool:
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
