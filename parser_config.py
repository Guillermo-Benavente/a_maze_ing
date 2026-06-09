from pydantic import BaseModel, Field, model_validator
from typing import Any
from random import randint
from sys import maxsize as maxs
from collections.abc import Callable
from algoritm import found_all, found_weight
from functools import partial
from sys import argv
from maze.config import MazeConfig


LIST = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT", "SEED",
        "ALGORITM", "VISUAL3D", "ALLWAYS"]


def asignate(_: list[list[Any]]) -> bool:
    """
    Placeholder validation callback rule for Pydantic
    ALGORITM instantiation.

    Args:
        _: list[list[Any]]): Mock environment nested cell structure.

    Returns:
        bool: Hardcoded evaluation rule confirmation flag (True).
    """
    return True


class Data(BaseModel):

    WIDTH: int = Field(..., gt=0, le=100)
    HEIGHT: int = Field(..., gt=0, le=100)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(..., min_length=5)
    PERFECT: bool
    VISUAL3D: bool
    SEED: int = Field(default_factory=lambda: randint(1, maxs))
    ALGORITM: Callable[..., Any] = Field(default=asignate)
    ALLWAYS: bool = Field(default=True)

    def to_maze_config(self) -> MazeConfig:
        """
        Transforms the current configuration instance state into a structured
        and validated MazeConfig data transfer object.

        Extracts structural properties, execution rules, orientation flags,
        and procedural generation properties to build a clean immutable
        mapping snapshot.

        Returns:
            MazeConfig: A fresh configuration data record instance matching
                        the active environment attributes.
        """
        return MazeConfig(
            WIDTH=self.WIDTH,
            HEIGHT=self.HEIGHT,
            ENTRY=self.ENTRY,
            EXIT=self.EXIT,
            OUTPUT_FILE=self.OUTPUT_FILE,
            PERFECT=self.PERFECT,
            VISUAL3D=self.VISUAL3D,
            SEED=self.SEED,
            ALGORITM=self.ALGORITM,
            ALLWAYS=self.ALLWAYS
        )

    @model_validator(mode="before")
    @classmethod
    def parser(cls, data_3d: dict[str, str]) -> dict[str, Any]:
        """
        Pre-evaluates configuration string datasets, casting value types
        and resolving application parameters before model parsing.

        Args:
            data_3d (dict[str, str]): Raw input values parsed from
                configuration readouts.

        Returns:
            dict[str, Any]: Typed settings mapping ready for model injection.
        """
        entry = (0, 0)
        exits = (0, 0)
        sol: dict[str, Any] = {}
        if isinstance(data_3d.get("ALLWAYS"), str):
            allWays = data_3d["ALLWAYS"].lower()
            assert (allWays == "true"
                    or allWays == "false"), "ALLWAYS is icorrect"
            sol.update({"ALLWAYS": allWays == "true"})
        if isinstance(data_3d.get("WIDTH"), str):
            sol.update({"WIDTH": int(data_3d["WIDTH"])})
        if isinstance(data_3d.get("HEIGHT"), str):
            sol.update({"HEIGHT": int(data_3d["HEIGHT"])})
        if isinstance(data_3d.get("SEED"), str):
            sol.update({"SEED": int(data_3d["SEED"])})
        if isinstance(data_3d.get("ENTRY"), str):
            x, y = data_3d["ENTRY"].strip("()").split(",")
            entry = (int(x), int(y))
            sol.update({"ENTRY": entry})
        if isinstance(data_3d.get("EXIT"), str):
            x, y = data_3d["EXIT"].strip("()").split(",")
            exits = (int(x), int(y))
            sol.update({"EXIT": exits})
        if isinstance(data_3d.get("OUTPUT_FILE"), str):
            assert argv[1] != data_3d["OUTPUT_FILE"], ("the output and input"
                                                       " is the same")
            sol.update({"OUTPUT_FILE": data_3d["OUTPUT_FILE"]})
        if isinstance(data_3d.get("PERFECT"), str):
            value = data_3d["PERFECT"].lower()
            assert value == "true" or value == "false", "PERFECT is icorrect"
            sol.update({"PERFECT": value == "true"})
        if isinstance(data_3d.get("ALGORITM"), str):
            algoritm = int(data_3d["ALGORITM"])
            assert algoritm == 1 or algoritm == 2, "ALGORITM not found"
            if algoritm == 1:
                sol.update({"ALGORITM": partial(
                    found_all,
                    entry,
                    exits,
                    allWays == "true")})
            else:
                sol.update({"ALGORITM": partial(
                    found_weight,
                    entry,
                    exits,
                    allWays == "true")})
        if isinstance(data_3d.get("VISUAL3D"), str):
            value = data_3d["VISUAL3D"].lower()
            assert value == "true" or value == "false", "VISUAL3D is icorrect"
            sol.update({"VISUAL3D": value == "true"})
        return sol

    @model_validator(mode="after")
    def check_entry(self) -> "Data":
        """
        Post-initialization logical validator asserting dimension constraints,
        distinct entry/exit cells, and output naming conventions.

        Returns:
            Data: The validated state representation containing certified
                configuration details.
        """
        x, y = self.ENTRY
        assert 0 <= x < self.WIDTH, "ENTRY: x fuera de rango"
        assert 0 <= y < self.HEIGHT, "ENTRY: y fuera de rango"
        x2, y2 = self.EXIT
        assert 0 <= x2 < self.WIDTH, "EXIT: x fuera de rango"
        assert 0 <= y2 < self.HEIGHT, "EXIT: y fuera de rango"
        assert x2 != x or y2 != y, "EXIT: is the same that ENTRY"
        assert self.OUTPUT_FILE.endswith(".txt"), "OUTPUT_FILE isn't a txt"
        if isinstance(self.ALGORITM([[]]), bool):
            self.ALGORITM = partial(
                found_all,
                self.ENTRY,
                self.EXIT,
                self.ALLWAYS)
        return self


def lector(archive: str) -> dict[str, str]:
    """
    Reads a dedicated key-value text sheet mapping rules for grid
    configuration, filtering remarks and ensuring no identifier repeats.

    Args:
        archive (str): Relative or global string target file path.

    Raises:
        FileNotFoundError: If the designated document path does not exist.
        ValueError: If file syntax parsing requirements are violated.

    Returns:
        dict[str, str]: Isolated configuration identifiers associated
            with string configurations.
    """
    sol: dict[str, str] = {}
    try:
        with open(archive, "r") as fd:
            content = fd.read()
            contents = content.split("\n")
    except FileNotFoundError:
        raise FileNotFoundError(f"'{archive}' doesn't exist")
    for part in contents:
        parts = part.split("=")
        if part.startswith("#"):
            pass
        elif part and len(parts) == 2 and parts[0] and parts[1]:
            assert parts[0] in LIST, "Bad Sintax"
            assert not parts[0] in sol, "Not duplicate permit"
            sol.update({parts[0].strip(" "): parts[1].strip(" ")})
        elif part:
            raise ValueError("Bad Sintax")
    return sol
