from typing import Callable, Any, Generator
from maze.cell import Cell
from numpy import abs


def operate(num: Cell, thinks: list[tuple[str, int, int]],
            order: list[tuple[str, int, int]]
            ) -> list[tuple[str, int, int]]:

    if not num.walls.north:
        order.append(thinks[0])
    if not num.walls.east:
        order.append(thinks[1])
    if not num.walls.south:
        order.append(thinks[2])
    if not num.walls.west:
        order.append(thinks[3])
    return order


def generateweight(local: tuple[int, int], exits: tuple[int, int]) -> int:
    x, y = local
    ex, ey = exits
    return int(abs(x - ex) + abs(y - ey))


def operate2(num: Cell, thinks: list[tuple[str, int, int]],
             order: list[tuple[str, int, int]],
             exits: tuple[int, int], pos: tuple[int, int],
             weight: int
             ) -> list[tuple[str, int, int]]:
    operations: list[dict[str, Any]] = []
    lis = [
        not num.walls.north,
        not num.walls.east,
        not num.walls.south,
        not num.walls.west
    ]

    for n in range(len(thinks)):
        _, x, y = thinks[n]
        operations.append({"weight": generateweight((x, y), exits),
                           "thinks": thinks[n], "operate": lis[n]})

    operations = sorted(operations, key=lambda x: x["weight"])
    for elements in operations:
        if elements["operate"]:
            order.append(elements["thinks"])
    return order


def found_all(enter: tuple[int, int], exits: tuple[int, int],
              maps: list[list[Cell]]) -> dict[str, Callable[..., Any]]:
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    dirs = [(('N', 0, -1)), (('E', 1, 0)), (('S', 0, 1)), (('W', -1, 0))]

    def algoritm(text: str = "", x: int = enx, y: int = eny,
                 visited: set[tuple[int, int]] = set()
                 ) -> Generator[str, None, None]:
        nonlocal texts
        if len(text) == 0:
            texts = []
            visited.clear()
        order: list[tuple[str, int, int]] = []
        if len(text) != 0:
            yield text
        if x == exix and y == exiy:
            texts.append(text)
            return
        if (x, y) in visited:
            return
        visited.add((x, y))
        num = maps[y][x]
        order = operate(num, dirs, order)
        for te, xx, yy in order:
            yield from algoritm(text + te, x + xx, y + yy, visited)

    def sorter() -> str:
        sol = sorted(texts, key=lambda x: len(x))
        return sol[0]

    def lista() -> list[str]:
        sol = sorted(texts, key=lambda x: len(x))
        return sol

    funtul: dict[str, Callable[..., Any]] = {
        "algoritm": algoritm,
        "list": lista,
        "sorter": sorter
    }
    return funtul


def found_weight(enter: tuple[int, int], exits: tuple[int, int],
                 maps: list[list[Cell]]) -> dict[str, Callable[..., Any]]:
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    dirs = [('N', 0, -1), ('E', 1, 0), ('S', 0, 1), ('W', -1, 0)]

    def algoritm(text: str = "", x: int = enx, y: int = eny,
                 visited: set[tuple[int, int]] = set()
                 ) -> Generator[str, None, None]:
        nonlocal texts
        if len(text) == 0:
            texts = []
            visited.clear()
        order: list[tuple[str, int, int]] = []
        if len(text) != 0:
            yield text
        if x == exix and y == exiy:
            texts.append(text)
            return
        if (x, y) in visited:
            return
        visited.add((x, y))
        num = maps[y][x]
        order = operate2(num, dirs, order, (exix, exiy),
                         (x, y), int(abs(x - exix) + abs(y - exiy)))
        for te, xx, yy in order:
            yield from algoritm(text + te, x + xx, y + yy, visited)

    def sorter() -> str:
        return lista()[0]

    def lista() -> list[str]:
        sol = sorted(texts, key=lambda x: len(x))
        return sol

    funtul: dict[str, Callable[..., Any]] = {
        "algoritm": algoritm,
        "list": lista,
        "sorter": sorter
    }
    return funtul
