from enum import Enum, auto

class CellType(Enum):
    NORMAL = auto()
    LIMIT = auto()
    ENTRY = auto()
    EXIT = auto()
    FORTY_TWO = auto()

class LimitWallType(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()