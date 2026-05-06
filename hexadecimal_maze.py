from random import choice, seed
from parser_config import Data
from enum import Enum

class NodeType(Enum):
    NORMAL = 0
    LIMIT = 1
    ENTRY = 2
    EXIT = 3
    FORTY_TWO = 4

class Direction():
    north: bool
    east: bool
    south: bool
    west: bool

    def __init__(self) -> None:
        self.north = False
        self.east = False
        self.south = False
        self.west = False
    
    def bin(self) -> list[str]:
        return [
            f"{int(self.north)}",
            f"{int(self.east)}",
            f"{int(self.south)}",
            f"{int(self.west)}"
        ]
    
    def all(self) -> None:
        self.north = True
        self.east = True
        self.south = True
        self.west = True

class Node():
    value: str
    position: tuple[int, int]
    type_node: NodeType
    limits: Direction

    def __init__(
        self,
        position: tuple[int, int],
        type_node: NodeType,
        direction: Direction
    ) -> None:
        self.position = position
        self.type_node = type_node
        self.limits = direction
        self.generate_values()

    def generate_values(self) -> None:
        north: str = '1' if self.limits.north else '0'
        east: str = '1' if self.limits.east else '0'
        south: str = '1' if self.limits.south else '0'
        west: str = '1' if self.limits.west else '0'
        bits: str = north + east + south + west
        self.value = f"{int(bits, 2):x}".upper()


class Maze():
    maze: list[list[Node]]
    data: Data
    def __init__(self, data: Data) -> None:
        self.maze: list[list[Node]] = [
            [
                Node((y, x), NodeType.NORMAL, Direction()) 
                for x in range(data.WIDTH)
            ] 
            for y in range(data.HEIGHT)
        ]
        self.data = data
        seed(data.SEED)
        self._create_maze()

    def _create_maze(self) -> None:
        if self.data.WIDTH < 7 or self.data.HEIGHT < 5:
            raise Exception("size too small")
        self._create_forty_two()
        self._create_limits()
        self._create_walls()

    def _create_walls(self):
        pos: list[int] = range(32)
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                node: Node = self.maze[height][width]
                if node.type_node != NodeType.FORTY_TWO:
                    direction = Direction()
                    value: int = choice(pos)
                    walls: str = f"{value % 8:04b}"
                    if node.type_node == NodeType.LIMIT:
                        direction.north = (bool(int(walls[0])) or node.limits.north)
                        direction.east = (bool(int(walls[1])) or node.limits.east)
                        direction.south = (bool(int(walls[2])) or node.limits.south)
                        direction.west = (bool(int(walls[3])) or node.limits.west)
                    else:
                        direction.north = bool(int(walls[0]))
                        direction.east = bool(int(walls[1]))
                        direction.south = bool(int(walls[2]))
                        direction.west = bool(int(walls[3]))
                    node.limits = direction
                    node.generate_values()


    def _create_limits(self) -> None:
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                if (
                    height == 0 or
                    width == 0 or
                    height == self.data.HEIGHT - 1 or
                    width == self.data.WIDTH - 1
                ):
                    direction = Direction()
                    if height == 0:
                        direction.north = True
                    if width == 0:
                        direction.west = True
                    if height == self.data.HEIGHT - 1:
                        direction.south = True
                    if width == self.data.WIDTH - 1:
                        direction.east = True
                    self.maze[height][width].type_node = NodeType.LIMIT
                    self.maze[height][width].limits = direction
                    self.maze[height][width].generate_values()

    def _create_forty_two(self) -> None:
        height: int = (self.data.HEIGHT // 2) - 2
        width: int = (self.data.WIDTH // 2) - 3
        for i in range(5):
            for j in range(7):
                if (
                    j != 3 and
                    not (i == 0 and (j == 1 or j == 2)) and
                    not (i == 1 and 1 <= j <= 5) and
                    not (i == 3 and j in [0, 1, 5, 6]) and
                    not (i == 4 and (j == 0 or j == 1))
                ):
                    direction: Direction = Direction()
                    direction.all()
                    self.maze[height + i][width + j].type_node = NodeType.FORTY_TWO
                    self.maze[height + i][width + j].limits = direction
                    self.maze[height + i][width + j].generate_values()
    
    def view_maze(self) -> None:
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                print(self.maze[height][width].value, end="")
            print()