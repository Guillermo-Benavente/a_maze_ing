from typing import Callable, Any


def operate(num: int, thinks: tuple[str, int, int],
            order: list[tuple[str, int, int]]
            ) -> tuple[int, list[tuple[str, int, int]]]:
    if num % 10 == 0:
        order.append(thinks)
    num //= 10
    return (num, order)


def found_all(maps: list[list[str]], enter: tuple[int, int],
              exits: tuple[int, int]) -> dict[str, Callable[..., Any]]:
    texts: list[str] = []
    enx, eny = enter
    exix, exiy = exits
    visited = set()
    dictionary: dict[str, int] = {
        "0": 0,
        "1": 1,
        "2": 10,
        "3": 11,
        "4": 100,
        "5": 101,
        "6": 110,
        "7": 111,
        "8": 1000,
        "9": 1001,
        "A": 1010,
        "B": 1011,
        "C": 1100,
        "D": 1101,
        "E": 1110,
        "F": 1111
    }

    def algoritm(text: str = "", x: int = enx, y: int = eny,
                 prex: int = -10, prey: int = -10) -> None:
        order: list[tuple[str, int, int]] = []
        if x == exix and y == exiy:
            texts.append(text)
            return
        if (x, y) in visited:
            return
        visited.add((x, y))
        num = dictionary[maps[y][x]]
        num, order = operate(num, ("N", 0, -1), order)
        num, order = operate(num, ("E", 1, 0), order)
        num, order = operate(num, ("S", 0, 1), order)
        num, order = operate(num, ("W", -1, 0), order)
        for te, xx, yy in order:
            algoritm(text + te, x + xx, y + yy, x, y)
        visited.remove((x, y))

    def lista() -> str:
        sol = sorted(texts, key=lambda x: len(x))
        return sol

    funtul = {
        "algoritm": algoritm,
        "list": lista
    }
    return funtul


if __name__ == "__main__":
    hola = """9515391539551795151151153
EBABAE812853C1412BA812812
96A8416A84545412AC4282C2A
C3A83816A9395384453A82D02
96842A852AC07AAD13A8283C2
C1296C43AAB83AA92AA8686BA
92E853968428444682AC12902
AC3814452FA83FFF82C52C42A
85684117AFC6857FAC1383D06
C53AD043AFFFAFFF856AA8143
91441294297FAFD501142C6BA
AA912AC3843FAFFF82856D52A
842A8692A92B8517C4451552A
816AC384468285293917A9542
C416928513C443A828456C3BA
91416AA92C393A82801553AAA
A81292AA814682C6A8693C6AA
A8442C6C2C1168552C16A9542
86956951692C1455416928552
C545545456C54555545444556"""
    fil = hola.split("\n")
    mapa = []
    for i in fil:
        mapa.append(list(i))
    alle = found_all(mapa, (1, 1), (19, 14))
    alle["algoritm"]()
    print(alle["list"]())
