from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from random import randint
from sys import maxsize as maxs


@dataclass
class MazeConfig:
    """
    Lightweight standalone configuration dataclass for the maze generation
    pipeline.

    Provides validated grid dimension constraints, spatial coordinate
    boundaries for entry and exit cells, and optional solver algorithm
    selection. Designed as a self-contained replacement for the Pydantic
    ``Data`` model to allow the ``maze`` module to be used independently
    without external dependencies.

    Attributes:
        WIDTH (int): Total horizontal cell count of the maze grid
            (1 to 100).
        HEIGHT (int): Total vertical cell count of the maze grid
            (1 to 100).
        ENTRY (tuple[int, int]): Starting position coordinates
            ``(x, y)`` within grid bounds.
        EXIT (tuple[int, int]): Target destination coordinates
            ``(x, y)`` distinct from the entry point.
        OUTPUT_FILE (str): File path string ending with ``.txt`` for
            writing hexadecimal maze output. Defaults to ``"maze.txt"``.
        PERFECT (bool): Generate a perfect maze with exactly one
            solution path (True) or an imperfect maze with multiple
            loops and alternative routes (False). Defaults to True.
        VISUAL3D (bool): Flag indicating 3D raycasting rendering
            mode; skips solver computation when True. Defaults
            to False.
        SEED (int): Pseudo-random generator seed value for
            reproducible maze layouts. Auto-generated from a random
            range if not explicitly provided.
        ALGORITM (Callable[..., Any] | None): Solver algorithm factory
            accepting a maze grid and returning a solver dictionary.
            When ``None`` and ``VISUAL3D`` is False, the solution
            path computation is skipped. Defaults to None.
    """
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = "maze.txt"
    PERFECT: bool = True
    VISUAL3D: bool = False
    SEED: int = field(default_factory=lambda: randint(1, maxs))
    ALGORITM: Callable[..., Any] | None = None

    def __post_init__(self) -> None:
        """
        Validates configuration bounds and coherence constraints after
        instance initialisation.

        Confirms grid dimensions are within the acceptable 1-to-100
        range, both entry and exit coordinates fall inside the grid
        boundaries, the two points are distinct, and the output file
        name carries the required ``.txt`` extension.

        Raises:
            AssertionError: If any validation constraint is violated,
                with a descriptive message indicating the specific
                field and reason.
        """
        assert 1 <= self.WIDTH <= 100, "WIDTH must be between 1 and 100"
        assert 1 <= self.HEIGHT <= 100, "HEIGHT must be between 1 and 100"
        x, y = self.ENTRY
        assert 0 <= x < self.WIDTH, "ENTRY x out of range"
        assert 0 <= y < self.HEIGHT, "ENTRY y out of range"
        x2, y2 = self.EXIT
        assert 0 <= x2 < self.WIDTH, "EXIT x out of range"
        assert 0 <= y2 < self.HEIGHT, "EXIT y out of range"
        assert (x2, y2) != (x, y), "EXIT must differ from ENTRY"
        assert self.OUTPUT_FILE.endswith(".txt"), (
            "OUTPUT_FILE must end with .txt"
        )
