from .enums import CellType, LimitWallType
from .wall import Wall


class Cell():
    """
    Represents an individual grid node within the maze structure,
    managing its properties and encoding.
    """
    hexadecimal: str
    binary: int
    zone_id: int | None
    position: tuple[int, int]
    cell_type: list[CellType]
    limit_wall_type: list[LimitWallType]
    walls: Wall

    def __init__(self, position: tuple[int, int]) -> None:
        """
        Initializes a maze cell at a specific coordinate and
        triggers its initial wall hexadecimal encoding.
        Args:
            position (tuple[int, int]): The (x, y) coordinates
            of the cell in the grid.
        """
        self.position = position
        self.binary = 0
        self.zone_id = None
        self.cell_type = []
        self.walls = Wall()
        self.limit_wall_type = []
        self.encode_walls()

    def encode_walls(self) -> None:
        """
        Calculates a bitmask based on active walls and converts
        it into a single uppercase hexadecimal character.

        Bit encoding follows the subject specification:
            Bit 0 (LSB) — North
            Bit 1       — East
            Bit 2       — South
            Bit 3       — West
        A closed wall sets the bit to 1; an open wall sets it to 0.
        """
        self.binary = 0
        if self.walls.north:
            self.binary |= 1
        if self.walls.east:
            self.binary |= 2
        if self.walls.south:
            self.binary |= 4
        if self.walls.west:
            self.binary |= 8
        self.hexadecimal = f"{self.binary:x}".upper()
