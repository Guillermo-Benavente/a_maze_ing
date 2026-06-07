from typing import Callable, Any, Generator
from maze.cell import Cell
from numpy import abs


def operate(num: Cell, thinks: list[tuple[str, int, int]],
            order: list[tuple[str, int, int]]
            ) -> list[tuple[str, int, int]]:
    """
    Evaluates which walls of a cell are open (North, East, South, West)
    and appends the corresponding directionaltuples to the allowed order list.

    Args:
        num (Cell): The target maze cell being inspected.
        thinks (list[tuple[str, int, int]]): Base directional
            offset tuples (N, E, S, W).
        order (list[tuple[str, int, int]]): The accumulation list
            where valid movements are added.

    Returns:
        list[tuple[str, int, int]]: The updated list containing
            the available valid paths.
    """
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
    """
    Calculates the Manhattan distance heuristic from a localized position
    to the designated exit cell of the maze.

    Args:
        local (tuple[int, int]): Current spatial coordinates (x, y).
        exits (tuple[int, int]): Target exit coordinates (x, y).

    Returns:
        int: The calculated total Manhattan weight or remaining
            distance estimate.
    """
    x, y = local
    ex, ey = exits
    return int(abs(x - ex) + abs(y - ey))


def operate2(num: Cell, thinks: list[tuple[str, int, int]],
             order: list[tuple[str, int, int]],
             exits: tuple[int, int], pos: tuple[int, int]
             ) -> list[tuple[str, int, int]]:
    """
    Evaluates open adjacent cells similar to `operate`, but sorts the
    resulting movements by prioritizing choices that reduce
    Manhattan distance to the exit.

    Args:
        num (Cell): The target maze cell being inspected.
        thinks (list[tuple[str, int, int]]): Base directional offset
            tuples (N, E, S, W).
        order (list[tuple[str, int, int]]): The accumulation list where
            sorted movements are added.
        exits (tuple[int, int]): Target exit coordinates of the maze.
        pos (tuple[int, int]): Current absolute coordinates before
            applying offsets.

    Returns:
        list[tuple[str, int, int]]: Movement tuples sorted from
            lowest to highest heuristic weight.
    """
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
    """
    Solves the maze using a standard Depth-First Search (DFS) backtracker.
    Explores paths sequentially without a heuristic weight priority.

    Args:
        enter (tuple[int, int]): The starting point coordinates (x, y).
        exits (tuple[int, int]): The destination exit coordinates (x, y).
        maps (list[list[Cell]]): The entire 2D matrix structure of the maze.

    Returns:
        dict[str, Callable[..., Any]]: A dictionary containing operational
            handles for:
                - "algoritm": The step-by-step path Generator.
                - "list": Method to retrieve all successful solution paths.
                - "sorter": Method to fetch the shortest solution path.
    """
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    dirs = [(('N', 0, -1)), (('E', 1, 0)), (('S', 0, 1)), (('W', -1, 0))]

    def algoritm() -> Generator[str, None, None]:
        """
        Executes a stack-based DFS traversal. Yields string step
        streams and records completed paths upon hitting target
        exit points.

        Yields:
            str: Accumulated character direction log step up to the
                current cell frame.
        """
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
        """
        Sorts discovered paths by character string length and returns
        the shortest path.

        Returns:
            str: The path string requiring the fewest directional steps.
        """
        return lista()[0]

    def lista() -> list[str]:
        """
        Collects and sorts all valid found solution path strings by
        total length.

        Returns:
            list[str]: An ordered collection of path solutions.
        """
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
    """
    Solves the maze via an informed Depth-First Search strategy by prioritizing
    open nodes that feature a smaller Manhattan distance weight towards the
    destination.

    Args:
        enter (tuple[int, int]): The starting point coordinates (x, y).
        exits (tuple[int, int]): The destination exit coordinates (x, y).
        maps (list[list[Cell]]): The entire 2D matrix structure of the maze.

    Returns:
        dict[str, Callable[..., Any]]: A dictionary containing operational
            handles for:
                - "algoritm": The step-by-step heuristic Generator.
                - "list": Method to retrieve all successful solution paths.
                - "sorter": Method to fetch the shortest solution path.
    """
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    dirs = [('N', 0, -1), ('E', 1, 0), ('S', 0, 1), ('W', -1, 0)]

    def algoritm() -> Generator[str, None, None]:
        """
        Executes a stack-based informed traversal. Yields string step
        streams and records completed paths upon hitting target
        exit points.

        Yields:
            str: Accumulated character direction log step up to the
                current cell frame.
        """
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
        """
        Sorts discovered paths by character string length and returns
        the shortest path.

        Returns:
            str: The path string requiring the fewest directional
                steps.
        """
        return lista()[0]

    def lista() -> list[str]:
        """
        Collects and sorts all valid found solution path strings by
        total length.

        Returns:
            list[str]: An ordered collection of path solutions.
        """
        sol = sorted(texts, key=lambda x: len(x))
        return sol

    funtul: dict[str, Callable[..., Any]] = {
        "algoritm": algoritm,
        "list": lista,
        "sorter": sorter
    }
    return funtul
