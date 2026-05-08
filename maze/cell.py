from .enums import CellType, LimitWallType
from .wall import Wall

class Cell():
    hexadecimal: str
    binary: int
    miner_id: int | None
    position: tuple[int, int]
    cell_type: list[CellType]
    limit_wall_type: list[LimitWallType]
    walls: Wall

    def __init__(self, position: tuple[int, int]) -> None:
        self.position = position
        self.binary = 0
        self.miner_id = None
        self.cell_type = []
        self.walls = Wall()
        self.limit_wall_type = []
        self.encode_walls()

    def encode_walls(self) -> None:
        self.binary = 0
        if self.walls.north:
            self.binary |= 8
        if self.walls.east:
            self.binary |= 4
        if self.walls.south:
            self.binary |= 2
        if self.walls.west:
            self.binary |= 1
        self.hexadecimal = f"{self.binary:x}".upper()