from typing import Callable, Any, Generator
from maze.cell import Cell


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


def found_all(enter: tuple[int, int], exits: tuple[int, int],
              maps: list[list[Cell]]) -> dict[str, Callable[..., Any]]:
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    dirs = [(('N', 0, -1)), (('E', 1, 0)), (('S', 0, 1)), (('W', -1, 0))]

    def algoritm(text: str = "", x: int = enx, y: int = eny,
                 visited: set = set()) -> Generator[str, None, None]:
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

    def lista() -> str:
        sol = sorted(texts, key=lambda x: len(x))
        return sol

    funtul = {
        "algoritm": algoritm,
        "list": lista
    }
    return funtul
