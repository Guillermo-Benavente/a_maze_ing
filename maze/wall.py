class Wall():
    north: bool
    east: bool
    south: bool
    west: bool

    def __init__(self) -> None:
        self.north = True
        self.east = True
        self.south = True
        self.west = True
    
    def bin(self) -> list[str]:
        return [
            f"{int(self.north)}",
            f"{int(self.east)}",
            f"{int(self.south)}",
            f"{int(self.west)}"
        ]