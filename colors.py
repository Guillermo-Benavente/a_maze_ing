from enum import Enum


class Colors():
    __pos: int
    __color: list[tuple[int, int, int, int]]

    def __init__(self, color: list[tuple[int, int, int, int]]) -> None:
        self.__pos = 0
        self.__color = color

    def get_pos(self) -> int:
        return self.__pos

    def get_color(self) -> tuple[int, int, int, int]:
        return self.__color[self.get_pos()]

    def _set_pos(self, pos: int) -> None:
        self.__pos = pos


class Acolors():
    color: list[Colors] = []

    __wall = [
        (0x3D, 0x2B, 0x1F, 0xFF),
        (0x7A, 0x63, 0x52, 0xFF),
        (0x2E, 0xCC, 0x71, 0xFF),
        (0xE7, 0x4C, 0x3C, 0xFF),
        (0xB8, 0x86, 0x0B, 0xFF)
    ]

    __floor = [
        (0x1A, 0x47, 0x26, 0xFF),
        (0x8B, 0x69, 0x14, 0xFF),
        (0xF0, 0xE0, 0x40, 0xFF),
        (0x9B, 0x59, 0xB6, 0xFF),
        (0xE8, 0xA0, 0xBF, 0xFF)
    ]

    __entrance = [
        (0x0D, 0x0D, 0x2B, 0xFF),
        (0x1C, 0x1C, 0x3A, 0xFF),
        (0x00, 0xCf, 0xFF, 0xFF),
        (0xFF, 0x6B, 0x00, 0xFF),
        (0xA8, 0x55, 0xF7, 0xFF)
    ]

    __exits = [
        (0x6B, 0x4C, 0x2A, 0xFF),
        (0xD4, 0xA9, 0x6A, 0xFF),
        (0x3A, 0xAF, 0xA9, 0xFF),
        (0xC0, 0x39, 0x2B, 0xFF),
        (0xF5, 0xF0, 0xE8, 0xFF)
    ]

    __way = [
        (0x2C, 0x4A, 0x6E, 0xFF),
        (0xA8, 0xC8, 0xE8, 0xFF),
        (0xF4, 0xD0, 0x3F, 0xFF),
        (0xE9, 0x1E, 0x8C, 0xFF),
        (0x1D, 0xE3, 0xB0, 0xFF)
    ]

    lista = [__wall, __floor, __entrance, __exits, __way]

    def __init__(self) -> None:
        for i in Acolors.lista:
            self.color.append(Colors(i))

    def _all_colors(self) -> None:
        for i in self.color:
            self.__incrementcolor(i)

    def _evol_color(self, pos: int) -> None:
        self.__incrementcolor(self.color[pos])

    def __incrementcolor(self, color: Colors) -> None:
        if color.get_pos() == 4:
            color._set_pos(0)
            return
        color._set_pos(color.get_pos() + 1)

    def get_color(self, pos: int) -> tuple[int, int, int, int]:
        if 0 <= pos <= 4:
            return self.color[pos].get_color()
        return (0, 0, 0, 0)


class All_colors():
    al: Acolors
    lista: list[Colors] = []
    number42 = [
        [
            (0xF0, 0xF0, 0xF0, 0xFF),
            (0xFF, 0xFD, 0xE7, 0xFF),
            (0xE0, 0xFA, 0xFF, 0xFF),
            (0xFF, 0xF8, 0xE1, 0xFF),
            (0xF8, 0xFB, 0xFF, 0xFF)
        ],
        [
            (0x1A, 0x0A, 0x00, 0xFF),
            (0x0A, 0x1F, 0x0D, 0xFF),
            (0x05, 0x05, 0x10, 0xFF),
            (0x1C, 0x0D, 0x00, 0xFF),
            (0x08, 0x0F, 0x18, 0xFF)
        ]
    ]

    def __init__(self) -> None:
        self.al = Acolors()
        for i in self.number42:
            self.lista.append(Colors(i))

    def __evol_this(self) -> None:
        self.__incrementcolor(self.lista[0])
        self.__incrementcolor(self.lista[1])

    def evol_color(self, pos: int) -> None:
        if 0 <= pos <= 4:
            self.al._evol_color(pos)
        self.__evol_this()

    def __incrementcolor(self, color: Colors) -> None:
        if color.get_pos() == 4:
            color._set_pos(0)
            return
        color._set_pos(color.get_pos() + 1)

    def get_color(self, pos: int) -> tuple[int, int, int, int]:
        if 0 <= pos <= 4:
            return self.al.get_color(pos)
        if 6 == pos or pos == 7:
            return self.lista[pos - 6].get_color()
        return (0, 0, 0, 0)

    def all_colors(self) -> None:
        self.al._all_colors()
        self.evol_color(5)


class ColorCell(Enum):
    WALL = 0
    FLOOR = 1
    ENTRY = 2
    EXIT = 3
    WAY = 4
    WALL_42 = 6
    FLOOR_42 = 7
