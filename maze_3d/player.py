from butons import Buttons as but
from math import sin, cos
from maze_3d.data_3d import *
from maze_3d.mapa import Mapa
from mlx_py import MlxPy

class Player:

    def __init__(self, setings: Data_3D, mapa: Mapa) -> None:
        self.x = (setings.data.ENTRY[0] + 0.5) * setings.CELS_SIZE
        self.y = (setings.data.ENTRY[1] + 0.5) * setings.CELS_SIZE
        self.setings = setings
        self.mapa = mapa
        self.radius = 3

        self.rotationAngle = 45 * (pi / 180)

        self.turnDirection = 0
        self.walkDirection = 0

        self.moveSpeed = 2.5
        self.rotationSpeed = 2 * (pi / 180)

    def _blocked_x(self, new_x: float) -> bool:
        cel = self.setings.CELS_SIZE
        r = self.radius
        w = self.setings.data.WIDTH
        h = self.setings.data.HEIGHT

        if new_x < r or new_x >= w * cel - r:
            return True

        y_top = max(0, int((self.y - r) // cel))
        y_bot = min(h - 1, int((self.y + r) // cel))
        x_left = int((new_x - r) // cel)
        x_right = int((new_x + r) // cel)

        for my in range(y_top, y_bot + 1):
            for mx in range(max(0, x_left), min(w, x_right + 1)):
                cell = self.mapa.maze[my][mx]
                if cell.walls.east and new_x + r > (mx + 1) * cel:
                    return True
                if cell.walls.west and new_x - r < mx * cel:
                    return True
        return False

    def _blocked_y(self, new_y: float) -> bool:
        cel = self.setings.CELS_SIZE
        r = self.radius
        w = self.setings.data.WIDTH
        h = self.setings.data.HEIGHT

        if new_y < r or new_y >= h * cel - r:
            return True

        x_left = max(0, int((self.x - r) // cel))
        x_right = min(w - 1, int((self.x + r) // cel))
        y_top = int((new_y - r) // cel)
        y_bot = int((new_y + r) // cel)

        for my in range(max(0, y_top), min(h, y_bot + 1)):
            for mx in range(x_left, x_right + 1):
                cell = self.mapa.maze[my][mx]
                if cell.walls.south and new_y + r > (my + 1) * cel:
                    return True
                if cell.walls.north and new_y - r < my * cel:
                    return True
        return False

    def update(self, keys: list[int], param: MlxPy) -> None:
        _ = param

        self.walkDirection = 0
        self.turnDirection = 0
        for key in keys:
            if key in (but.BUTTON_UP.value, but.BUTTON_W.value, but.BUTTON_NUMPATH_8.value):
                self.walkDirection = 1
            if key in (but.BUTTON_DOWN.value, but.BUTTON_S.value, but.BUTTON_NUMPATH_2.value):
                self.walkDirection = -1
            if key in (but.BUTTON_RIGHT.value, but.BUTTON_D.value, but.BUTTON_NUMPATH_6.value):
                self.turnDirection = 1
            if key in (but.BUTTON_LEFT.value, but.BUTTON_A.value, but.BUTTON_NUMPATH_4.value):
                self.turnDirection = -1

        moveStep = self.walkDirection * self.moveSpeed
        self.rotationAngle += self.turnDirection * self.rotationSpeed
        movex = cos(self.rotationAngle) * moveStep
        movey = sin(self.rotationAngle) * moveStep
        new_x = self.x + movex
        new_y = self.y + movey
        if movex != 0 and not self._blocked_x(new_x):
            self.x = new_x
        if movey != 0 and not self._blocked_y(new_y):
            self.y = new_y
        # print(self.x)
        # print(self.y)
        # i = (self.rotationAngle * (180 / pi)) % 360
        # if i < 0:
        #     i += 360
        # print(i, end="\n\n")
