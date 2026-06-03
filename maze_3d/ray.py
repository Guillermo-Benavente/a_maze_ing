from .map import Map
from .player import Player
from dataclasses import dataclass
from math import sqrt, tan, cos, pi


def normalize_angle(angle: float) -> float:
    angle = angle % (2 * pi)
    if angle <= 0:
        angle = (2 * pi) + angle
    return angle


def distance_between(x1: float, y1: float, x2: float, y2: float) -> float:
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


@dataclass
class RayOrientation:
    angle: float
    is_up: bool
    is_down: bool
    is_left: bool
    is_right: bool

    @classmethod
    def from_angle(cls, angle: float) -> 'RayOrientation':
        normalized = normalize_angle(angle)
        is_down = 0.0 < normalized < pi
        is_up = not is_down
        is_left = 0.5 * pi <= normalized <= 1.5 * pi
        is_right = not is_left
        return cls(normalized, is_up, is_down, is_left, is_right)


@dataclass
class RayHit:
    x: float = 0.0
    y: float = 0.0
    distance: float = 0.0
    side: str = ""


class Ray:
    colors1: tuple[int, int, int, int]
    colors2: tuple[int, int, int, int]
    current_color: tuple[int, int, int, int]
    orientation: RayOrientation
    hit: RayHit
    player: Player
    map: Map

    def __init__(
        self,
        angle: float,
        player: Player,
        map: Map,
        colors1: tuple[int, int, int, int],
        colors2: tuple[int, int, int, int]
    ) -> None:
        self.colors1 = colors1
        self.colors2 = colors2
        self.current_color = colors1
        self.player = player
        self.map = map
        self.orientation = RayOrientation.from_angle(angle)
        self.hit = RayHit()

    def _find_horizontal_intersection(
        self,
        cell_size: int,
        map_width: int,
        map_height: int
    ) -> tuple[bool, float, float]:
        player_x: float = self.player.transform.x
        player_y: float = self.player.transform.y
        first_intercept_y: float = player_y
        first_intercept_x: float = player_x
        ray_angle: float = self.orientation.angle
        if self.orientation.is_up:
            first_intercept_y = (player_y // cell_size) * cell_size - 0.0001
        elif self.orientation.is_down:
            first_intercept_y = (
                ((player_y // cell_size) * cell_size) + cell_size
            )
        if tan(ray_angle) != 0:
            first_intercept_x = (
                player_x + (first_intercept_y - player_y) / tan(ray_angle)
            )
        step_y: float = -cell_size if self.orientation.is_up else cell_size
        step_x: float = step_y / tan(ray_angle) if tan(ray_angle) != 0 else 0.0
        wall_side: str = "S" if self.orientation.is_up else "N"
        return self._ray_loop_scan(
            first_intercept_x, first_intercept_y,
            step_x, step_y,
            map_width, map_height,
            wall_side
        )

    def _find_vertical_intersection(
        self,
        cell_size: int,
        map_width: int,
        map_height: int
    ) -> tuple[bool, float, float]:
        player_x: float = self.player.transform.x
        player_y: float = self.player.transform.y
        first_intercept_x: float = player_x
        ray_angle: float = self.orientation.angle
        if self.orientation.is_left:
            first_intercept_x = (player_x // cell_size) * cell_size - 0.0001
        elif self.orientation.is_right:
            first_intercept_x = (
                ((player_x // cell_size) * cell_size) + cell_size
            )
        first_intercept_y: float = (
            player_y + (first_intercept_x - player_x) * tan(ray_angle)
        )
        step_x: float = -cell_size if self.orientation.is_left else cell_size
        step_y: float = step_x * tan(ray_angle)
        wall_side: str = "E" if self.orientation.is_left else "W"
        return self._ray_loop_scan(
            first_intercept_x, first_intercept_y,
            step_x, step_y,
            map_width, map_height,
            wall_side
        )

    def _ray_loop_scan(
        self,
        start_x: float,
        start_y: float,
        step_x: float,
        step_y: float,
        map_width: int,
        map_height: int,
        wall_direction: str
    ) -> tuple[bool, float, float]:
        cell_size: int = self.map.setings.CELS_SIZE
        while (
            (-cell_size <= start_x < map_width + cell_size)
            and (-cell_size <= start_y < map_height + cell_size)
        ):
            if self.map.has_wall_at(start_x, start_y, wall_direction):
                return True, start_x, start_y
            start_x += step_x
            start_y += step_y
        return False, 0.0, 0.0

    def cast(self) -> None:
        MAX_DISTANCE: float = 999999.0
        cell_size: int = self.map.setings.CELS_SIZE
        map_width: int = self.map.setings.data.WIDTH * cell_size
        map_height: int = self.map.setings.data.HEIGHT * cell_size
        player_x: float = self.player.transform.x
        player_y: float = self.player.transform.y
        [
            found_horizontal,
            horiz_hit_x,
            horiz_hit_y
        ] = self._find_horizontal_intersection(
            cell_size, map_width, map_height
        )
        [
            found_vertical,
            vert_hit_x,
            vert_hit_y
        ] = self._find_vertical_intersection(
            cell_size, map_width, map_height
        )
        dist_horizontal: float = (
            distance_between(player_x, player_y, horiz_hit_x, horiz_hit_y)
            if found_horizontal
            else MAX_DISTANCE
        )
        dist_vertical: float = (
            distance_between(player_x, player_y, vert_hit_x, vert_hit_y)
            if found_vertical
            else MAX_DISTANCE
        )
        if dist_horizontal < dist_vertical:
            self.hit.x = horiz_hit_x
            self.hit.y = horiz_hit_y
            self.hit.distance = dist_horizontal
            self.current_color = self.colors2
            self.hit.side = "S" if self.orientation.is_up else "N"
        else:
            self.hit.x = vert_hit_x
            self.hit.y = vert_hit_y
            self.hit.distance = dist_vertical
            self.current_color = self.colors1
            self.hit.side = "E" if self.orientation.is_left else "W"
        self.hit.distance *= cos(
            self.player.transform.rotation_angle - self.orientation.angle
        )
