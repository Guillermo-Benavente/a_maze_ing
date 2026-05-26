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


class BaseColors():
    color: list[Colors] = []

    __wall = [
        (0x3A, 0x8B, 0x20, 0xFF),
        (0x51, 0x6F, 0xE7, 0xFF),
        (0x86, 0x4E, 0x09, 0xFF),
        (0x17, 0x35, 0x4F, 0xFF),
        (0x69, 0x61, 0x57, 0xFF)
    ]

    __floor = [
        (0x31, 0x8E, 0xF7, 0xFF),
        (0x71, 0x72, 0x28, 0xFF),
        (0xAB, 0x87, 0xFF, 0xFF),
        (0x48, 0x67, 0x5E, 0xFF),
        (0x5C, 0x75, 0xD0, 0xFF)
    ]

    __entrance = [
        (0x21, 0x6B, 0xF2, 0xFF),
        (0x53, 0x46, 0x26, 0xFF),
        (0x8F, 0x5D, 0xFF, 0xFF),
        (0x18, 0x36, 0x28, 0xFF),
        (0x2B, 0x35, 0x88, 0xFF)
    ]

    __exits = [
        (0x40, 0xB0, 0xFB, 0xFF),
        (0x8F, 0x9D, 0x2A, 0xFF),
        (0xC1, 0xA6, 0xFF, 0xFF),
        (0x78, 0x98, 0x93, 0xFF),
        (0xB1, 0xCE, 0xEB, 0xFF)
    ]

    __way = [
        (0x52, 0xEC, 0xFC, 0xFF),
        (0x7D, 0xB1, 0x8A, 0xFF),
        (0xF5, 0xF5, 0xF5, 0xFF),
        (0xA7, 0xCB, 0xD8, 0xFF),
        (0xDE, 0xE9, 0xEE, 0xFF)
    ]

    lista = [__wall, __floor, __entrance, __exits, __way]

    def __init__(self) -> None:
        for i in BaseColors.lista:
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


class AllColors():
    al: BaseColors
    lista: list[Colors] = []
    number42 = [
        [
            (0x3C, 0xCA, 0x99, 0xFF),
            (0x61, 0xA2, 0xF4, 0xFF),
            (0x91, 0x5E, 0x1F, 0xFF),
            (0x16, 0x3B, 0x5A, 0xFF),
            (0x79, 0x81, 0x79, 0xFF)
        ],
        [
            (0x47, 0xDB, 0xCB, 0xFF),
            (0x6A, 0xC4, 0xE9, 0xFF),
            (0xB8, 0x81, 0x3D, 0xFF),
            (0x46, 0x6C, 0x86, 0xFF),
            (0x89, 0x94, 0x92, 0xFF)
        ]
    ]

    def __init__(self) -> None:
        self.al = BaseColors()
        for i in self.number42:
            self.lista.append(Colors(i))

    def __evol_this(self) -> None:
        self.__incrementcolor(self.lista[0])
        self.__incrementcolor(self.lista[1])

    def evol_color(self, pos: int) -> None:
        if 0 <= pos <= 4:
            self.al._evol_color(pos)
        else:
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
