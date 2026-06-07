class Wall():
    """
    Represents the physical boundaries (four walls)
    surrounding a single maze cell.
    """
    north: bool
    east: bool
    south: bool
    west: bool

    def __init__(self) -> None:
        """
        Initializes a new Wall instance with all four
        directional walls active by default.
        """
        self.north = True
        self.east = True
        self.south = True
        self.west = True

    def bin(self) -> list[str]:
        """
        Converts the boolean states of the walls into a
        list of binary string representations ('1' or '0').

        Returns:
            list[str]: Array elements containing string '1' for closed
                walls, '0' for open.
        """
        return [
            f"{int(self.north)}",
            f"{int(self.east)}",
            f"{int(self.south)}",
            f"{int(self.west)}"
        ]
