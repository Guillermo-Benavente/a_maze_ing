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
             exits: tuple[int, int], pos: tuple[int, int]
             ) -> list[tuple[str, int, int]]:
    operations: list[dict[str, Any]] = []
    lis = [
        not num.walls.north,
        not num.walls.east,
        not num.walls.south,
        not num.walls.west
    ]

    x, y = pos
    for n in range(len(thinks)):
        _, xp, yp = thinks[n]
        operations.append({"weight": generateweight((x + xp, y + yp), exits),
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

    def algoritm() -> Generator[str, None, None]:
        nonlocal texts
        texts = []
        visited: set[tuple[int, int]] = set()
        num_inicial = maps[eny][enx]
        vecinos_iniciales = operate(num_inicial, dirs, [])
        stack = [("", enx, eny, vecinos_iniciales, 0)]
        while stack:
            text, x, y, order, index = stack[-1]
            if index == 0:
                if len(text) != 0:
                    yield text
                if x == exix and y == exiy:
                    texts.append(text)
                    stack.pop()
                    continue
                if (x, y) in visited:
                    stack.pop()
                    continue
                visited.add((x, y))
            if index >= len(order):
                visited.remove((x, y))
                stack.pop()
                continue
            stack[-1] = (text, x, y, order, index + 1)
            te, xx, yy = order[index]
            nx, ny = x + xx, y + yy
            if (nx, ny) not in visited:
                num_sig = maps[ny][nx]
                vecinos_sig = operate(num_sig, dirs, [])
                stack.append((text + te, nx, ny, vecinos_sig, 0))

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

    def algoritm() -> Generator[str, None, None]:
        nonlocal texts
        texts = []
        visited: set[tuple[int, int]] = set()
        num_inicial = maps[eny][enx]
        vecinos_iniciales = operate2(num_inicial, dirs, [], exits, enter)
        stack = [("", enx, eny, vecinos_iniciales, 0)]
        while stack:
            text, x, y, order, index = stack[-1]
            if index == 0:
                if len(text) != 0:
                    yield text
                if x == exix and y == exiy:
                    texts.append(text)
                    stack.pop()
                    continue
                if (x, y) in visited:
                    stack.pop()
                    continue
                visited.add((x, y))
            if index >= len(order):
                visited.remove((x, y))
                stack.pop()
                continue
            stack[-1] = (text, x, y, order, index + 1)
            te, xx, yy = order[index]
            nx, ny = x + xx, y + yy
            if (nx, ny) not in visited:
                num_sig = maps[ny][nx]
                vecinos_sig = operate2(num_sig, dirs, [], exits, (x, y))
                stack.append((text + te, nx, ny, vecinos_sig, 0))

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
