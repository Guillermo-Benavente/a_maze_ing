from maze.cell import Cell
from datas import Datas

class Mapa():
	def __init__(self, maze: list[list[Cell]], setings: Datas) -> None:
		self.maze = maze
		self.setings = setings
	
	def has_wall_at(self, x: float, y: float) -> Cell:
		tile = self.setings.TILE_SIZE
		return self.maze[int(y // tile)][int(x // tile)]
