from ray import Ray, Player, Mapa
from mlx_py import MlxPy

class Raycaster:
	def __init__(self, player: Player, mapa: Mapa):
		self.rays = []
		self.player = player
		self.mapa = mapa
	
	def castAllRays(self) -> None:
		self.rays = []

		rayAngle = (self.player.rotationAngle - self.mapa.setings.FOV / 2)
		for _ in range(self.mapa.setings.NUM_RAYS):
			ray = Ray(rayAngle, self.player, self.mapa)
			ray.cast()
			self.rays.append(ray)
			rayAngle += self.mapa.setings.FOV / self.mapa.setings.NUM_RAYS

	def render(self, mlx: MlxPy) -> None:
		i = 0
		for ray in self.rays:
			#formula matematica para calcular la distancia
			line_height = (self.mapa.setings.TILE_SIZE / ray.distance) * 415
			draw_begin = (self.mapa.setings.WINDOW_HEIGHT / 2) - (line_height / 2)
			draw_end = line_height
			res = self.mapa.setings.RES
			mlx.flat_canvas.draw_rectangle(i * res, draw_begin, res, draw_end, ray.colors)
