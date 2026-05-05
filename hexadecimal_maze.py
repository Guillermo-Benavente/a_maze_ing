from random import choice, seed
from parser_config import Data
from enum import Enum

class NodeType(Enum):
    NORMAL = 0
    LIMIT = 1
    ENTRY = 2
    EXIT = 3
    FORTY_TWO = 4

class Node():
    MAX_HEIGHT: int = 0
    MAX_WIDTH: int = 0

    value: str
    position: tuple[int, int]
    type_node: NodeType
    limits: list[int]

    def __init__(self, position: tuple[int, int], type_node: NodeType):
        self.position = position
        self.type_node = type_node
        self._generate_values()

    @classmethod
    def set_bounds(cls, height, width):
        cls.MAX_HEIGHT = height
        cls.MAX_WIDTH = width

    def _generate_values(self):
        match self.type_node:
            case NodeType.NORMAL:
                self.value = '0'
            case NodeType.LIMIT:
                x, y = self.position[0], self.position[1]
                max_y = self.MAX_HEIGHT - 1
                max_x = self.MAX_WIDTH - 1
                north = '1' if y == 0 else '0'
                east = '1' if x == max_x else '0'
                south = '1' if y == max_y else '0'
                west = '1' if x == 0 else '0'
                bits = north + east + south + west
                self.value = f"{int(bits, 2):x}".upper()
                self.limits = [int(bit) for bit in bits]
            case NodeType.FORTY_TWO:
                self.value = 'F'


class Maze():
    maze: list[list[Node]]
    data: Data
    def __init__(self, data: Data):
        Node.set_bounds(data.HEIGHT, data.WIDTH)
        self.maze: list[list[Node]] = [
            [
                Node((y, x), NodeType.NORMAL) 
                for x in range(data.WIDTH)
            ] 
            for y in range(data.HEIGHT)
        ]
        self.data = data

    def create_maze(self):
        if self.data.WIDTH < 7 or self.data.HEIGHT < 5:
            raise Exception("size too small")
        self._create_forty_two()
        self._create_limits()

    def _create_limits(self):
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                if (
                    height == 0 or
                    width == 0 or
                    height == self.data.HEIGHT - 1 or
                    width == self.data.WIDTH - 1
                ):
                    self.maze[height][width] = Node((width, height), NodeType.LIMIT)

    def _create_forty_two(self):
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
                    self.maze[height + i][width + j] = Node((width + j, height + i), NodeType.FORTY_TWO)
    
    def view_maze(self):
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                print(self.maze[height][width].value, end="")
            print()