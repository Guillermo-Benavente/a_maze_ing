from maze_3d.ray import Ray, Player, Mapa
from mlx_py import MlxPy

class Raycaster:
    def __init__(self, player: Player, mapa: Mapa,
                 color: tuple[int, int, int, int],
                 color1: tuple[int, int, int, int],
                 floor: tuple[int, int, int, int]):
        self.rays = []
        self.player = player
        self.mapa = mapa
        self.color = color
        self.color1 = color1
        self.floor = floor
    
    def castAllRays(self) -> None:
        self.rays = []

        rayAngle = (self.player.rotationAngle - self.mapa.setings.VISION / 2)
        for _ in range(self.mapa.setings.NUM_RAYS):
            ray = Ray(rayAngle, self.player, self.mapa, self.color, self.color1)
            ray.cast()
            self.rays.append(ray)
            rayAngle += self.mapa.setings.VISION / self.mapa.setings.NUM_RAYS

    def render(self, mlx: MlxPy) -> None:
        i = 0
        mlx.flat_canvas.draw_rectangle(0, 0, self.mapa.setings.WINDOW_WIDTH, self.mapa.setings.WINDOW_HEIGHT //2 , (0, 0, 0, 0xFF))
        mlx.flat_canvas.draw_rectangle(0, self.mapa.setings.WINDOW_HEIGHT //2, self.mapa.setings.WINDOW_WIDTH, self.mapa.setings.WINDOW_HEIGHT, self.floor)
        for ray in self.rays:
            line_height = (self.mapa.setings.CELS_SIZE / ray.distance) * 415
            draw_begin = (self.mapa.setings.WINDOW_HEIGHT / 2) - (line_height / 2)
            draw_end = line_height
            resolution = self.mapa.setings.RESOLUTION
            if draw_begin < 0:
                draw_end += draw_begin
                draw_begin = 0
            if draw_end > self.mapa.setings.WINDOW_HEIGHT:
                draw_end = self.mapa.setings.WINDOW_HEIGHT
            mlx.flat_canvas.draw_rectangle(
                int(i * resolution),
                int(draw_begin),
                int(resolution),
                int(draw_end),
                ray.colors
            )
            i += 1
