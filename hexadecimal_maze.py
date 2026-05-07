from random import choice, seed
from parser_config import Data
from enum import Enum

class NodeType(Enum):
    NORMAL = 0
    LIMIT = 1
    ENTRY = 2
    EXIT = 3
    FORTY_TWO = 4

class LimitType(Enum):
    NONE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

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
    type_node: list[NodeType]
    limit_type: list[LimitType]
    limits: Direction

    def __init__(
        self,
        position: tuple[int, int],
        type_node: NodeType,
        direction: Direction
    ) -> None:
        self.position = position
        self.type_node = [type_node]
        self.limits = direction
        self.limit_type = [LimitType.NONE]
        self.generate_values()

    def generate_values(self) -> None:
        bits: int = 0
        if self.limits.north:
            bits |= 8
        if self.limits.east:
            bits |= 4
        if self.limits.south:
            bits |= 2
        if self.limits.west:
            bits |= 1
        self.value = f"{bits:x}".upper()


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
        posibilities: list[int] = range(32)

        if self.data.WIDTH < 7 or self.data.HEIGHT < 5:
            raise Exception("size too small")
        self._create_forty_two()
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                self._create_limits(height, width)
                self._search_inout(height, width)
                self._create_walls(height, width, posibilities)
        self._join_walls()
        
    def _join_walls(self):
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                node: Node = self.maze[height][width]
                if LimitType.EAST not in node.limit_type:
                    east: Node = self.maze[height][width + 1]
                    if NodeType.FORTY_TWO in east.type_node:
                        node.limits.east = east.limits.west
                    else:
                        east.limits.west = node.limits.east
                    east.generate_values()
                if LimitType.SOUTH not in node.limit_type:
                    south: Node = self.maze[height + 1][width]
                    if NodeType.FORTY_TWO in south.type_node:
                        node.limits.south = south.limits.north
                    else:
                        south.limits.north = node.limits.south
                    south.generate_values()
                node.generate_values()
                if node.value == 'F' and NodeType.FORTY_TWO not in node.type_node:
                    self._break_random_wall(height, width)

    def _break_random_wall(self, h: int, w: int):
        node = self.maze[h][w]
        possible_to_break = []
        if h > 0 and NodeType.FORTY_TWO not in self.maze[h-1][w].type_node:
            possible_to_break.append("north")
        if h < self.data.HEIGHT - 1 and NodeType.FORTY_TWO not in self.maze[h+1][w].type_node:
            possible_to_break.append("south")
        if w < self.data.WIDTH - 1 and NodeType.FORTY_TWO not in self.maze[h][w+1].type_node:
            possible_to_break.append("east")
        if w > 0 and NodeType.FORTY_TWO not in self.maze[h][w-1].type_node:
            possible_to_break.append("west")

        if possible_to_break:
            chosen = choice(possible_to_break)
            if chosen == "north":
                node.limits.north = False
                self.maze[h-1][w].limits.south = False
                self.maze[h-1][w].generate_values()
            elif chosen == "south":
                node.limits.south = False
                self.maze[h+1][w].limits.north = False
                self.maze[h+1][w].generate_values()
            elif chosen == "east":
                node.limits.east = False
                self.maze[h][w+1].limits.west = False
                self.maze[h][w+1].generate_values()
            elif chosen == "west":
                node.limits.west = False
                self.maze[h][w-1].limits.east = False
                self.maze[h][w-1].generate_values()
            
            node.generate_values()

    def _create_walls(self, height: int, width: int, posibilities: list[int]):
        node: Node = self.maze[height][width]

        if NodeType.FORTY_TWO not in node.type_node:
            direction = Direction()
            value: int = choice(posibilities)
            walls: str = f"{value % 8:04b}"

            if NodeType.LIMIT in node.type_node:
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

    def _search_inout(self, height: int, width: int):
        if (
            self.data.ENTRY[0] == width and
            self.data.ENTRY[1] == height
        ):
            self.maze[height][width].type_node.append(NodeType.ENTRY)
        elif (
            self.data.EXIT[0] == width and
            self.data.EXIT[1] == height
        ):
            self.maze[height][width].type_node.append(NodeType.EXIT)

    def _create_limits(self, height: int, width: int) -> None:
        node: Node = self.maze[height][width]

        if (
            height == 0 or
            width == 0 or
            height == self.data.HEIGHT - 1 or
            width == self.data.WIDTH - 1
        ):
            direction = Direction()
            
            node.limit_type = []
            if height == 0:
                direction.north = True
                node.limit_type.append(LimitType.NORTH)
            if width == 0:
                direction.west = True
                node.limit_type.append(LimitType.WEST)
            if height == self.data.HEIGHT - 1:
                direction.south = True
                node.limit_type.append(LimitType.SOUTH)
            if width == self.data.WIDTH - 1:
                direction.east = True
                node.limit_type.append(LimitType.EAST)
            if NodeType.FORTY_TWO not in node.type_node:
                node.type_node = [NodeType.LIMIT]
                node.limits = direction
                node.generate_values()
            else:
                node.type_node.append(NodeType.LIMIT)

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
                    self.maze[height + i][width + j].type_node = [NodeType.FORTY_TWO]
                    self.maze[height + i][width + j].limits = direction
                    self.maze[height + i][width + j].generate_values()
    
    def view_maze(self) -> None:
        for height in range(self.data.HEIGHT):
            for width in range(self.data.WIDTH):
                print(self.maze[height][width].value, end="")
            print()
    
    def view_maze_ascii(self) -> None:
        for height in range(self.data.HEIGHT):
            line_n = "" # Fila para techos (Norte)
            line_c = "" # Fila para centros (Oeste, contenido, Este)
            line_s = "" # Fila para suelos (Sur)
            
            for width in range(self.data.WIDTH):
                node = self.maze[height][width]
                val_hex = node.value
                val_int = int(val_hex, 16)
                
                # Bits: N=8, E=4, S=2, W=1
                n = bool(val_int & 8)
                e = bool(val_int & 4)
                s = bool(val_int & 2)
                w = bool(val_int & 1)
                
                # 1. Construcción del Techo (Norte)
                line_n += "+" + ("---" if n else "   ") + "+"
                
                # 2. Construcción del Centro (Oeste, Valor/Tipo, Este)
                char_w = "|" if w else " "
                char_e = "|" if e else " "
                
                # Identificación por tipo de nodo
                if NodeType.ENTRY in node.type_node:
                    content = f"({val_hex})"
                elif NodeType.EXIT in node.type_node:
                    content = f"[{val_hex}]"
                elif NodeType.FORTY_TWO in node.type_node:
                    content = " 42"
                else:
                    content = f" {val_hex} "
                
                line_c += char_w + content + char_e
                
                # 3. Construcción del Suelo (Sur)
                line_s += "+" + ("---" if s else "   ") + "+"

            # Imprimimos las tres líneas del bloque de celdas
            print(line_n)
            print(line_c)
            print(line_s)
