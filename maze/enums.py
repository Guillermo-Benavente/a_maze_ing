from enum import Enum, auto


class CellType(Enum):
    """
    An enumeration mapping structural classification and identity markers
    to individual cells within the maze layout matrix.
    """
    LIMIT = auto()
    """
    Indicates a boundary or border cell at the edge of the grid layout.
    """

    ENTRY = auto()
    """
    Indicates the designated starting or ingestion point of the maze structure.
    """

    EXIT = auto()
    """
    Indicates the target escape terminal or destination node of the maze.
    """

    FORTY_TWO = auto()
    """
    Indicates a special animated block containing custom thematic attributes.
    """


class LimitWallType(Enum):
    """
    An enumeration defining directional orientations for cell wall boundaries
    and multi-agent path exploration sweeps.
    """
    NORTH = auto()
    """
    Represents the upper vertical boundary relative to a cell frame.
    """

    EAST = auto()
    """
    Represents the right horizontal boundary relative to a cell frame.
    """

    SOUTH = auto()
    """
    Represents the lower vertical boundary relative to a cell frame.
    """

    WEST = auto()
    """
    Represents the left horizontal boundary relative to a cell frame.
    """
