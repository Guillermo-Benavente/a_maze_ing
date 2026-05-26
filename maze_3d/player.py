from butons import Buttons as but
from math import sin, cos
from datas import *
from mlx_py import MlxPy

class Player:

	def __init__(self, data: Data, setings: Datas) -> None:
		self.x = (data.ENTRY[0] + 0.5) * setings.TILE_SIZE
		self.y = (data.ENTRY[1] + 0.5) * setings.TILE_SIZE
		self.setings = setings
		self.radius = 3

		self.rotationAngle = 45 * (pi / 180)

		self.turnDirection = 0
		self.walkDirection = 0

		self.moveSpeed = 2.5
		self.rotationSpeed = 2 * (pi / 180)

	def update(self, key: int, param: MlxPy) -> None:
		_ = param
		self.turnDirection = 0
		self.walkDirection = 0

		if key in (but.BUTTON_UP, but.BUTTON_W, but.BUTTON_NUMPATH_8):
			self.walkDirection = 1
		if key in (but.BUTTON_DOWN, but.BUTTON_S, but.BUTTON_NUMPATH_2):
			self.walkDirection = -1
		if key in (but.BUTTON_RIGHT, but.BUTTON_D, but.BUTTON_NUMPATH_6):
			self.turnDirection = 1
		if key in (but.BUTTON_LEFT, but.BUTTON_A, but.BUTTON_NUMPATH_4):
			self.turnDirection = -1

		moveStep = self.walkDirection * self.moveSpeed
		self.rotationAngle += self.turnDirection * self.rotationSpeed
		self.x += cos(self.rotationAngle) * moveStep
		self.y += sin(self.rotationAngle) * moveStep
