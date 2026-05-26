from math import pi
from parser_config import Data

class Datas:
	
	def __init__(self, data: Data):
		self.data = data
		self.TILE_SIZE = 32
		self.WINDOW_WIDTH = data.WIDTH * self.TILE_SIZE
		self.WINDOW_HEIGHT = data.HEIGHT * self.TILE_SIZE 
		self.FOV = 60 * (pi / 180)
		self.RES = 4
		self.NUM_RAYS = self.WINDOW_WIDTH // self.RES