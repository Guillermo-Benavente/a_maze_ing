from .map import Map
from .player import Player
from dataclasses import dataclass
from math import sqrt, tan, cos, pi


def normalize_angle(angle: float) -> float:
    """
    Clamps a floating-point angle to fall strictly within the 0 to 2*pi radian
    range.

    Args:
        angle (float): The unnormalized input angle in radians.

    Returns:
        float: The normalized angle inside the interval (0, 2*pi].
    """
    angle = angle % (2 * pi)
    if angle <= 0:
        angle = (2 * pi) + angle
    return angle


def distance_between(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculates the Euclidean distance between two continuous 2D coordinate
    positions.

    Args:
        x1 (float): Horizontal position of the origin point.
        y1 (float): Vertical position of the origin point.
        x2 (float): Horizontal position of the target point.
        y2 (float): Vertical position of the target point.

    Returns:
        float: Linear spatial distance separating both coordinates.
    """
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


@dataclass
class RayOrientation:
    """
    Tracks and breaks down a vector's angular heading details.

    Acts as a boolean quadrant registry used to determine line-intercept steps
    and identify which grid cell faces are being approached.
    """
    angle: float
    """
    The normalized vector trajectory angle expressed in radians.
    """

    is_up: bool
    """
    True if the vector heads toward the upper/northern hemisphere of the map.
    """

    is_down: bool
    """
    True if the vector heads toward the lower/southern hemisphere of the map.
    """

    is_left: bool
    """
    True if the vector heads toward the left/western hemisphere of the map.
    """

    is_right: bool
    """
    True if the vector heads toward the right/eastern hemisphere of the map.
    """

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
    """
    Stores pinpoint metrics detailing a successful ray-to-obstacle collision
    point.
    """
    x: float = 0.0
    """
    Absolute horizontal coordinate where the intersection with a wall occurred.
    """

    y: float = 0.0
    """
    Absolute vertical coordinate where the intersection with a wall occurred.
    """

    distance: float = 0.0
    """
    Calculated length from the viewport camera to the intersection coordinate
    point.
    """

    side: str = ""
    """
    The specific structural wall face that was hit ('N', 'S', 'E', or 'W').
    """


class Ray:
    """
    Represents an isolated vector projected into a 2D layout to track walls.

    Employs Digital Differential Analysis (DDA) principles by projecting
    separate horizontal and vertical grid line cross-examinations, determining
    the closest collision point, and modifying raw depth outputs to counter
    fish-eye lens distortion.
    """
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
        """
        Initializes a distinct projection ray pointing toward a specific
        target angle.

        Args:
            angle (float): Target direction trajectory angle in radians.
            player (Player): Active viewpoint camera tracking context source.
            map (Map): Matrix layout structure wrapper containing cell
                coordinates.
            colors1 (tuple[int, int, int, int]): Default fallback color
                profile.
            colors2 (tuple[int, int, int, int]): Secondary color profile for
                alternative shading.
        """
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
        """
        Traces vector lines across horizontal grid rows to isolate cellular
        obstructions.

        Args:
            cell_size (int): Size dimensions assigned to individual square
                cells.
            map_width (int): Absolute horizontal bounds of the canvas.
            map_height (int): Absolute vertical bounds of the canvas.

        Returns:
            tuple[bool, float, float]: A status flag indicating if a wall was
                hit, along with the resulting (x, y) coordinates.
        """
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
        """
        Traces vector lines across vertical grid columns to isolate cellular
        obstructions.

        Args:
            cell_size (int): Size dimensions assigned to individual square
                cells.
            map_width (int): Absolute horizontal bounds of the canvas.
            map_height (int): Absolute vertical bounds of the canvas.

        Returns:
            tuple[bool, float, float]: A status flag indicating if a wall was
                hit, along with the resulting (x, y) coordinates.
        """
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
        """
        Advances the ray coordinates in fixed steps until a wall is encountered
        or the search exceeds map bounds.

        Args:
            start_x (float): Initial horizontal starting pixel intersection.
            start_y (float): Initial vertical starting pixel intersection.
            step_x (float): Horizontal index increment value applied per step.
            step_y (float): Vertical index increment value applied per step.
            map_width (int): Absolute horizontal maximum width limit.
            map_height (int): Absolute vertical maximum height limit.
            wall_direction (str): The cardinal edge facing identifier to test
                ('N', 'S', 'E', 'W').

        Returns:
            tuple[bool, float, float]: True along with the collision
                coordinates if a wall is found, otherwise False with
                (0.0, 0.0).
        """
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
        """
        Executes grid intersections along both axes and selects the closest
        valid collision.

        Applies a cosine correction based on the player's viewing angle to
        eliminate fish-eye lens distortion before submitting the final values.
        """
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
