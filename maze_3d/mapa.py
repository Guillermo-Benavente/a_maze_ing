from maze.cell import Cell
from maze_3d.datas import Datas

class Mapa():
    def __init__(self, maze: list[list[Cell]], setings: Datas) -> None:
        self.maze = maze
        self.setings = setings

    def has_wall_at(self, x: float, y: float, direction: str) -> Cell:
        cel = self.setings.CELS_SIZE
        map_x = int(x // cel)
        map_y = int(y // cel)
        if (map_x < 0 or map_x >= self.setings.data.WIDTH or map_y < 0 or
            map_y >= self.setings.data.HEIGHT):
            return True
        cell = self.maze[map_y][map_x]
        if direction == "N":
            return cell.walls.north
        if direction == "S":
            return cell.walls.south
        if direction == "E":
            return cell.walls.east
        if direction == "W":
            return cell.walls.west
