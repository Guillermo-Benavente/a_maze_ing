from butons import Buttons as but
from math import sin, cos
from maze_3d.datas import *
from mlx_py import MlxPy

class Player:

    def __init__(self, setings: Datas) -> None:
        self.x = (setings.data.ENTRY[0] + 0.5) * setings.CELS_SIZE
        self.y = (setings.data.ENTRY[1] + 0.5) * setings.CELS_SIZE
        self.setings = setings
        self.radius = 3

        self.rotationAngle = 45 * (pi / 180)

        self.turnDirection = 0
        self.walkDirection = 0

        self.moveSpeed = 2.5
        self.rotationSpeed = 2 * (pi / 180)

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
        if not ((movex + self.x) >= self.setings.data.WIDTH * self.setings.CELS_SIZE
                or (movex + self.x) <= 0):
            self.x += movex
        if not ((movey + self.y) >= self.setings.data.HEIGHT * self.setings.CELS_SIZE
                or (movey + self.y) <= 0):
            self.y += movey
        # print(self.x)
        # print(self.y)
        # i = (self.rotationAngle * (180 / pi)) % 360
        # if i < 0:
        #     i += 360
        # print(i, end="\n\n")
