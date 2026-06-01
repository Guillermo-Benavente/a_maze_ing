from maze_3d.ray import Ray, Player, Mapa
from mlx_py import MlxPy
from maze.enums import CellType


class Raycaster:
    def __init__(self, player: Player, mapa: Mapa,
                 wall_n: tuple[int, int, int, int],
                 wall_s: tuple[int, int, int, int],
                 wall_e: tuple[int, int, int, int],
                 wall_w: tuple[int, int, int, int],
                 floor: tuple[int, int, int, int],
                 floor_entry: tuple[int, int, int, int],
                 floor_exit: tuple[int, int, int, int],
                 floor_42: tuple[int, int, int, int],
                 wall_42: tuple[int, int, int, int]):
        self.rays = []
        self.center_ray = None
        self.player = player
        self.mapa = mapa
        self.wall_n = wall_n
        self.wall_s = wall_s
        self.wall_e = wall_e
        self.wall_w = wall_w
        self.floor = floor
        self.floor_entry = floor_entry
        self.floor_exit = floor_exit
        self.floor_42 = floor_42
        self.wall_42 = wall_42

    def castAllRays(self) -> None:
        self.rays = []

        rayAngle = (self.player.rotationAngle - self.mapa.setings.VISION / 2)
        for _ in range(self.mapa.setings.NUM_RAYS):
            ray = Ray(rayAngle, self.player, self.mapa, self.wall_n, self.wall_s)
            ray.cast()
            self.rays.append(ray)
            rayAngle += self.mapa.setings.VISION / self.mapa.setings.NUM_RAYS

        self.center_ray = Ray(self.player.rotationAngle, self.player, self.mapa, self.wall_n, self.wall_s)
        self.center_ray.cast()

    def _get_cell(self, ray: Ray) -> tuple[int, int]:
        cel = self.mapa.setings.CELS_SIZE
        return int(ray.wall_hit_x // cel), int(ray.wall_hit_y // cel)

    def _get_special_cell_color(self, cell) -> tuple[int, int, int, int] | None:
        if cell is None:
            return None
        if CellType.ENTRY in cell.cell_type:
            return self.floor_entry
        if CellType.EXIT in cell.cell_type:
            return self.floor_exit
        if CellType.FORTY_TWO in cell.cell_type:
            return self.wall_42
        return None

    def _neighbor_cell(self, ray: Ray) -> tuple[int, int] | None:
        mx, my = self._get_cell(ray)
        w = self.mapa.setings.data.WIDTH
        h = self.mapa.setings.data.HEIGHT
        if ray.hit_side == "S":
            return (mx, my + 1) if my + 1 < h else None
        if ray.hit_side == "N":
            return (mx, my - 1) if my - 1 >= 0 else None
        if ray.hit_side == "E":
            return (mx + 1, my) if mx + 1 < w else None
        if ray.hit_side == "W":
            return (mx - 1, my) if mx - 1 >= 0 else None
        return None

    def _get_wall_color(self, ray: Ray, cell) -> tuple[int, int, int, int]:
        if cell is not None:
            color = self._get_special_cell_color(cell)
            if color is not None:
                return color
        neighbor = self._neighbor_cell(ray)
        if neighbor is not None:
            nx, ny = neighbor
            color = self._get_special_cell_color(self.mapa.maze[ny][nx])
            if color is not None:
                return color
        return self._wall_color_by_side(ray)

    def _wall_color_by_side(self, ray: Ray) -> tuple[int, int, int, int]:
        return getattr(self, f"wall_{ray.hit_side.lower()}", self.wall_n)

    def _render_ray_strip(self, mlx: MlxPy, ray: Ray, x_pos: int, resolution: int) -> None:
        line_height = (self.mapa.setings.CELS_SIZE / ray.distance) * 415
        draw_begin = (self.mapa.setings.WINDOW_HEIGHT / 2) - (line_height / 2)
        draw_height = line_height

        if draw_begin < 0:
            draw_height += draw_begin
            draw_begin = 0
        if draw_begin + draw_height > self.mapa.setings.WINDOW_HEIGHT:
            draw_height = self.mapa.setings.WINDOW_HEIGHT - draw_begin

        mx, my = self._get_cell(ray)
        cell = self.mapa.maze[my][mx] if (0 <= mx < self.mapa.setings.data.WIDTH and 0 <= my < self.mapa.setings.data.HEIGHT) else None
        wall_color = self._get_wall_color(ray, cell)

        mlx.flat_canvas.draw_rectangle(
            x_pos,
            int(draw_begin),
            resolution,
            max(3, int(draw_height)),
            wall_color
        )

    def render(self, mlx: MlxPy) -> None:
        mlx.flat_canvas.draw_rectangle(0, 0, self.mapa.setings.WINDOW_WIDTH, self.mapa.setings.WINDOW_HEIGHT // 2, (0, 0, 0, 0xFF))
        mlx.flat_canvas.draw_rectangle(0, self.mapa.setings.WINDOW_HEIGHT // 2, self.mapa.setings.WINDOW_WIDTH, self.mapa.setings.WINDOW_HEIGHT, self.floor)

        resolution = self.mapa.setings.RESOLUTION
        for i, ray in enumerate(self.rays):
            self._render_ray_strip(mlx, ray, int(i * resolution), resolution)

        if self.center_ray:
            center_x = self.mapa.setings.WINDOW_WIDTH // 2 - resolution // 2
            self._render_ray_strip(mlx, self.center_ray, center_x, resolution)
