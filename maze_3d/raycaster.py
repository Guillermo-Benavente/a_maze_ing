from .ray import Ray
from .player import Player
from .map import Map
from mlx_py import MlxPy
from maze.enums import CellType
from maze.cell import Cell


class Raycaster:
    """
    Manages vector ray projection loops to build pseudo-3D views from a 2D
    grid.

    Coordinates multiple calculated Ray instances based on player perspective
    field of views, evaluates layout boundary intersections, resolves
    directional wall colors and textures, and paints horizontal pixel slices
    across the display output surface canvas.
    """
    rays: list[Ray]
    center_ray: Ray | None
    player: Player
    map: Map
    wall_n: tuple[int, int, int, int]
    wall_s: tuple[int, int, int, int]
    wall_e: tuple[int, int, int, int]
    wall_w: tuple[int, int, int, int]
    floor: tuple[int, int, int, int]
    floor_entry: tuple[int, int, int, int]
    floor_exit: tuple[int, int, int, int]
    floor_42: tuple[int, int, int, int]
    wall_42: tuple[int, int, int, int]

    def __init__(
        self, player: Player, map: Map,
        wall_n: tuple[int, int, int, int],
        wall_s: tuple[int, int, int, int],
        wall_e: tuple[int, int, int, int],
        wall_w: tuple[int, int, int, int],
        floor: tuple[int, int, int, int],
        floor_entry: tuple[int, int, int, int],
        floor_exit: tuple[int, int, int, int],
        floor_42: tuple[int, int, int, int],
        wall_42: tuple[int, int, int, int]
    ):
        """
        Initializes the pseudo-3D raycaster manager instance, mapping
        structural contexts and directional ambient shadow palettes.

        Args:
            player (Player): Active viewpoint coordinate camera and position
                source tracking token.
            map (Map): Core layout environment map wrapper containing cellular
                matrices.
            wall_n (tuple[int, int, int, int]): Active color mapping for
                northern wall intersections.
            wall_s (tuple[int, int, int, int]): Active color mapping for
                southern wall intersections.
            wall_e (tuple[int, int, int, int]): Active color mapping for
                eastern wall intersections.
            wall_w (tuple[int, int, int, int]): Active color mapping for
                western wall intersections.
            floor (tuple[int, int, int, int]): Active base floor rendering
                color mapping.
            floor_entry (tuple[int, int, int, int]): Structural entry point
                cellular floor overlay color.
            floor_exit (tuple[int, int, int, int]): Terminal escape point
                cellular floor overlay color.
            floor_42 (tuple[int, int, int, int]): Special animated '42'
                cellular floor surface overlay color.
            wall_42 (tuple[int, int, int, int]): Special animated '42'
                cellular boundary line outline color.
        """
        self.rays = []
        self.center_ray = None
        self.player = player
        self.map = map
        self.wall_n = wall_n
        self.wall_s = wall_s
        self.wall_e = wall_e
        self.wall_w = wall_w
        self.floor = floor
        self.floor_entry = floor_entry
        self.floor_exit = floor_exit
        self.floor_42 = floor_42
        self.wall_42 = wall_42

    def cast_all_rays(self) -> None:
        """
        Sweeps projection vectors uniformly across the camera's horizontal
        field of vision.

        Calculates distinct intersection depths for all slices matching window
        resolution settings, and fires an additional direct focal projection
        ray to compute pinpoint center-screen data.
        """
        self.rays = []
        settings = self.map.setings
        rotation: float = self.player.transform.rotation_angle
        ray_angle = rotation - (settings.VISION / 2)
        for _ in range(settings.NUM_RAYS):
            ray = Ray(
                ray_angle,
                self.player,
                self.map,
                self.wall_n,
                self.wall_s
            )
            ray.cast()
            self.rays.append(ray)
            ray_angle += settings.VISION / settings.NUM_RAYS
        self.center_ray = Ray(
            rotation,
            self.player,
            self.map,
            self.wall_n,
            self.wall_s
        )
        self.center_ray.cast()

    def _get_cell_indices(self, ray: Ray) -> tuple[int, int]:
        """
        Translates raw float spatial intersection coordinate pixels into
        discrete integer matrix index boundaries (x, y).

        Args:
            ray (Ray): Source vector tracking information container.

        Returns:
            tuple[int, int]: Mapped matrix indexes corresponding to grid cells.
        """
        cell_size = self.map.setings.CELS_SIZE
        return int(ray.hit.x // cell_size), int(ray.hit.y // cell_size)

    def _get_special_cell_color(
            self,
            cell: Cell
    ) -> tuple[int, int, int, int] | None:
        """
        Checks a cell's custom classification markers to see if it requires a
        special thematic color override.

        Args:
            cell (Cell): target cellular matrix structural unit.

        Returns:
            tuple[int, int, int, int] | None: Overridden RGBA color parameters,
                or None if it matches a standard asset.
        """
        if cell is None:
            return None
        if CellType.ENTRY in cell.cell_type:
            return self.floor_entry
        if CellType.EXIT in cell.cell_type:
            return self.floor_exit
        if CellType.FORTY_TWO in cell.cell_type:
            return self.wall_42
        return None

    def _get_neighbor_cell_indices(self, ray: Ray) -> tuple[int, int] | None:
        """
        Evaluates the step side direction of a ray intersection point and
        shifts parameters by 1 unit to isolate adjacent neighbor cells.

        Args:
            ray (Ray): Active calculated vector layout containing intersection
                properties.

        Returns:
            tuple[int, int] | None: Offset grid cell matrix coordinate pair,
                or None if shifting exceeds bounds.
        """
        map_x, map_y = self._get_cell_indices(ray)
        width = self.map.setings.data.WIDTH
        height = self.map.setings.data.HEIGHT
        match ray.hit.side:
            case "S":
                return (map_x, map_y + 1) if map_y + 1 < height else None
            case "N":
                return (map_x, map_y - 1) if map_y - 1 >= 0 else None
            case "E":
                return (map_x + 1, map_y) if map_x + 1 < width else None
            case "W":
                return (map_x - 1, map_y) if map_x - 1 >= 0 else None
            case _:
                return None

    def _get_wall_color(
            self,
            ray: Ray,
            cell: Cell | None
    ) -> tuple[int, int, int, int]:
        """
        Determines the display color of a wall section based on spatial
        orientation details and cell classification markers.

        Args:
            ray (Ray): Calculated vector tracking layout instance.
            cell (Cell | None): Target intersecting cell if valid, otherwise
                None.

        Returns:
            tuple[int, int, int, int]: The calculated destination BGRA color
                configuration tuple.
        """
        if cell is not None:
            color = self._get_special_cell_color(cell)
            if color is not None:
                return color
        neighbor = self._get_neighbor_cell_indices(ray)
        if neighbor is not None:
            nx, ny = neighbor
            color = self._get_special_cell_color(self.map.maze[ny][nx])
            if color is not None:
                return color
        return self._wall_color_by_side(ray)

    def _wall_color_by_side(self, ray: Ray) -> tuple[int, int, int, int]:
        """
        Routes active color arrays dynamically using string values from
        direction side labels.

        Args:
            ray (Ray): Source vector structural boundary element data tracker.

        Returns:
            tuple[int, int, int, int]: The directional color configuration
                tuple.
        """
        return getattr(self, f"wall_{ray.hit.side.lower()}", self.wall_n)

    def _render_ray_strip(
            self,
            mlx: MlxPy,
            ray: Ray,
            x_pos: int,
            resolution: int
    ) -> None:
        """
        Calculates wall slice scaling proportions using inverse distance
        ratios, and draws a single vertical strip on the display canvas.

        Args:
            mlx (MlxPy): Target display graphic abstraction layer package link.
            ray (Ray): Source vector configuration tracking properties.
            x_pos (int): Absolute horizontal pixel position along the
                rendering window frame.
            resolution (int): Render pixel layout column thickness width
                scaling boundaries.
        """
        settings = self.map.setings
        line_height = (settings.CELS_SIZE / ray.hit.distance) * 415
        draw_begin = (settings.WINDOW_HEIGHT / 2) - (line_height / 2)
        draw_height = line_height
        if draw_begin < 0:
            draw_height += draw_begin
            draw_begin = 0
        if draw_begin + draw_height > settings.WINDOW_HEIGHT:
            draw_height = settings.WINDOW_HEIGHT - draw_begin
        map_x, map_y = self._get_cell_indices(ray)
        if (0 <= map_x < settings.data.WIDTH and
           0 <= map_y < settings.data.HEIGHT):
            cell = self.map.maze[map_y][map_x]
        else:
            cell = None
        wall_color = self._get_wall_color(ray, cell)
        mlx.flat_canvas.draw_rectangle(
            x_pos,
            int(draw_begin),
            resolution,
            max(3, int(draw_height)),
            wall_color
        )

    def render(self, mlx: MlxPy) -> None:
        """
        Renders the pseudo-3D scene onto the canvas surface.

        Clears the view by painting the upper half as a solid sky box color
        (black) and the lower half as a solid floor color, then iterates
        through all cast rays to render individual wall column segments.

        Args:
            mlx (MlxPy): Target display pipeline graphics engine framework
                link.
        """
        settings = self.map.setings
        mlx.flat_canvas.draw_rectangle(
            0,
            0,
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT // 2,
            (0, 0, 0, 0xFF)
        )
        mlx.flat_canvas.draw_rectangle(
            0,
            settings.WINDOW_HEIGHT // 2,
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT,
            self.floor
        )
        resolution = settings.RESOLUTION
        for i, ray in enumerate(self.rays):
            self._render_ray_strip(mlx, ray, int(i * resolution), resolution)
        if self.center_ray:
            center_x = settings.WINDOW_WIDTH // 2 - resolution // 2
            self._render_ray_strip(mlx, self.center_ray, center_x, resolution)
