from math import pi
from parser_config import Data

class Datas:

    def __init__(self, data: Data):
        self.data = data
        self.CELS_SIZE = 32
        self.WINDOW_WIDTH = data.WIDTH * self.CELS_SIZE
        self.WINDOW_HEIGHT = data.HEIGHT * self.CELS_SIZE 
        self.VISION = 60 * (pi / 180)
        self.RESOLUTION = 8
        self.NUM_RAYS = self.WINDOW_WIDTH // self.RESOLUTION