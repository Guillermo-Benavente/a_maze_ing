from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Any
from random import randint
from sys import maxsize as maxs
from typing import Callable
from algoritm import found_all, found_pesos
from functools import partial


LIST = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT", "SEED", "ALGORITM"]


class Data(BaseModel):

    WIDTH: int = Field(..., gt=0)
    HEIGHT: int = Field(..., gt=0)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str = Field(..., min_length=5)
    PERFECT: bool
    SEED: int = Field(default_factory=lambda: randint(1, maxs))
    ALGORITM: Callable | None = None

    @model_validator(mode="before")
    @classmethod
    def parser(cls, datas: dict[str, str]) -> dict[str, Any]:
        entry = (0, 0)
        exits = (0, 0)
        sol: dict[str, Any] = {}
        if isinstance(datas.get("WIDTH"), str):
            sol.update({"WIDTH": int(datas["WIDTH"])})
        if isinstance(datas.get("HEIGHT"), str):
            sol.update({"HEIGHT": int(datas["HEIGHT"])})
        if isinstance(datas.get("SEED"), str):
            sol.update({"SEED": int(datas["SEED"])})
        if isinstance(datas.get("ENTRY"), str):
            x, y = datas["ENTRY"].strip("()").split(",")
            entry = (int(x), int(y))
            sol.update({"ENTRY": entry})
        if isinstance(datas.get("EXIT"), str):
            x, y = datas["EXIT"].strip("()").split(",")
            exits = (int(x), int(y))
            sol.update({"EXIT": exits})
        if isinstance(datas.get("OUTPUT_FILE"), str):
            sol.update({"OUTPUT_FILE": datas["OUTPUT_FILE"]})
        if isinstance(datas.get("PERFECT"), str):
            value = datas["PERFECT"].lower()
            assert value == "true" or value == "false", "PERFECT is icorrect"
            sol.update({"PERFECT": value == "true"})
        if isinstance(datas.get("ALGORITM"), str):
            algoritm = int(datas["ALGORITM"])
            assert algoritm == 1 or algoritm == 2, "ALGORITM not found"
            if algoritm == 1:
                sol.update({"ALGORITM": partial(found_all, entry, exits)})
            else:
                sol.update({"ALGORITM": partial(found_pesos, entry, exits)})
        return sol

    @model_validator(mode="after")
    def check_entry(self) -> "Data":
        x, y = self.ENTRY
        assert 0 <= x < self.WIDTH, "ENTRY: x fuera de rango"
        assert 0 <= y < self.HEIGHT, "ENTRY: y fuera de rango"
        x2, y2 = self.EXIT
        assert 0 <= x2 < self.WIDTH, "EXIT: x fuera de rango"
        assert 0 <= y2 < self.HEIGHT, "EXIT: y fuera de rango"
        assert x2 != x or y2 != y, "EXIT: is the same that ENTRY"
        assert self.OUTPUT_FILE.endswith(".txt"), "OUTPUT_FILE isn't a txt"
        if self.ALGORITM == None:
            self.ALGORITM = partial(found_all, self.ENTRY, self.EXIT)
        return self


def lector(archive: str) -> dict[str, str]:
    sol: dict[str, str] = {}
    with open(archive, "r") as fd:
        content = fd.read()
        contents = content.split("\n")
    for part in contents:
        parts = part.split("=")
        if part and len(parts) == 2 and parts[0] and parts[1]:
            assert parts[0] in LIST, "Bad Sintax"
            sol.update({parts[0].strip(" "): parts[1].strip(" ")})
        elif not part.startswith("#") and part:
            raise ValueError("Bad Sintax")
    return sol


if __name__ == "__main__":
    try:
        data = Data.model_validate(lector("config.txt"))
    except (ValidationError, ValueError, AssertionError, PermissionError) as e:
        if isinstance(e, ValidationError):
            for error in e.errors():
                print(error["msg"])
        else:
            print(e)
