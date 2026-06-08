from enum import Enum


class Colors():
    """
    Represents an individual dynamic color palette tracker.

    Manages an active index pointer to cycle sequentially through a designated
    list of internal RGBA color tuples.
    """
    __pos: int
    __color: list[tuple[int, int, int, int]]

    def __init__(self, color: list[tuple[int, int, int, int]]) -> None:
        """
        Initializes the color palette tracker, defaulting the index selection
        to 0.

        Args:
            color (list[tuple[int, int, int, int]]): A collection of
                structural BGRA color tuples.
        """
        self.__pos = 0
        self.__color = color

    def get_pos(self) -> int:
        """
        Retrieves the current active index pointer of this color palette.

        Returns:
            int: The current index selection value.
        """
        return self.__pos

    def get_color(self) -> tuple[int, int, int, int]:
        """
        Extracts the explicit RGBA color tuple corresponding to the
            active palette index.

        Returns:
            tuple[int, int, int, int]: The currently selected
                color tuple (B, G, R, A).
        """
        return self.__color[self.get_pos()]

    def _set_pos(self, pos: int) -> None:
        """
        Manually overrides the active color index position.

        Args:
            pos (int): The new target index position.
        """
        self.__pos = pos


class BaseColors():
    """
    Manages systemic background palettes for standard maze elements.

    Handles a structured mapping of color collections designated for walls,
    floors, entrances, exits, and solution pathways.
    """
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
        """
        Instantiates base tracking structures and populates the master list
        by wrapping raw element matrix variants into proper Colors objects.
        """
        for i in BaseColors.lista:
            self.color.append(Colors(i))

    def _all_colors(self) -> None:
        """
        Iterates through all registered base element types and advances
        their internal color palette selection index simultaneously.
        """
        for i in self.color:
            self.__incrementcolor(i)

    def _evol_color(self, pos: int) -> None:
        """
        Advances the color index pointer for a single target element type.

        Args:
            pos (int): The index identifying which category (e.g., WALL, FLOOR)
                to advance.
        """
        self.__incrementcolor(self.color[pos])

    def __incrementcolor(self, color: Colors) -> None:
        """
        Safely increments a palette's position index tracker, rolling back
        to 0 if it goes past the maximum available threshold.

        Args:
            color (Colors): The specific dynamic color entity instance to
                shift.
        """
        if color.get_pos() == 4:
            color._set_pos(0)
            return
        color._set_pos(color.get_pos() + 1)

    def get_color(self, pos: int) -> tuple[int, int, int, int]:
        """
        Retrieves the currently selected active RGBA color configuration tuple
        for a designated component position.

        Args:
            pos (int): The index referencing the target maze asset component.

        Returns:
            tuple[int, int, int, int]: The corresponding active BGRA color
                tuple, or transparent (0,0,0,0) if out of bounds.
        """
        if 0 <= pos <= 4:
            return self.color[pos].get_color()
        return (0, 0, 0, 0)


class AllColors():
    """
    The top-level orchestrator class linking and handling all active display
    palettes.

    Coordinates standard maze layouts alongside secondary special themes,
    such as the custom animated '42' cellular blocks.
    """
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
        """
        Initializes base configuration arrays, instantiates standard base
        palettes, and populates secondary tracking arrays with custom '42'
        thematic variations.
        """
        self.al = BaseColors()
        for i in self.number42:
            self.lista.append(Colors(i))

    def __evol_this(self) -> None:
        """
        Private routine triggering individual cyclical position index
        modifications exclusively for special '42' related asset themes.
        """
        self.__incrementcolor(self.lista[0])
        self.__incrementcolor(self.lista[1])

    def evol_color(self, pos: int) -> None:
        """
        Updates and shifts systemic color index paths depending on the
        requested input category.

        Delegates standard category updates down to BaseColors layers, or
        shifts '42' themes.

        Args:
            pos (int): The index identifier targeting which type of assets
                totransform.
        """
        if 0 <= pos <= 4:
            self.al._evol_color(pos)
        else:
            self.__evol_this()

    def __incrementcolor(self, color: Colors) -> None:
        """
        Safely increments a palette's position index tracker, rolling back
        to 0 if it goes past the maximum available threshold.

        Args:
            color (Colors): The specific dynamic color entity instance to
                shift.
        """
        if color.get_pos() == 4:
            color._set_pos(0)
            return
        color._set_pos(color.get_pos() + 1)

    def get_color(self, pos: int) -> tuple[int, int, int, int]:
        """
        Performs structural context mapping routing to retrieve active BGRA
        values across either standard base layers or specialized '42'
        component entities.

        Args:
            pos (int): The identifier targeting an explicitly requested cell
                state type.

        Returns:
            tuple[int, int, int, int]: The active color structure mapped to
                the component type, or transparent (0,0,0,0) if unmatched.
        """
        if 0 <= pos <= 4:
            return self.al.get_color(pos)
        if 6 == pos or pos == 7:
            return self.lista[pos - 6].get_color()
        return (0, 0, 0, 0)

    def all_colors(self) -> None:
        """
        Advances all registered asset palettes uniformly across the board
        by firing consecutive global shift operations.
        """
        self.al._all_colors()
        self.evol_color(5)


class ColorCell(Enum):
    """
    An enumeration system mapping categorical maze components
    to explicit positional layer offsets.
    """
    WALL = 0
    FLOOR = 1
    ENTRY = 2
    EXIT = 3
    WAY = 4
    WALL_42 = 6
    FLOOR_42 = 7
