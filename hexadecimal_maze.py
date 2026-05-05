from random import choice, seed
from parser_config import Data


class Node():
    value: str
    position: tuple[int, int]
    type_node: int
    limits: list[int]

    def __init__(self, position: tuple[int, int], type_node: int):
        self.position = position
        self.type_node = type_node
        


class maze():
    maze: list[list[str]]
    data: Data
    # hex(int('1010', 2))
    def __init__(self, data: Data):
        self.maze = []
        self.data = data

    def create_maze(self):
        self.create_struct()

    def create_struct(self):
        