from maze_3d.mapa import Mapa
from maze_3d.player import Player, pi
from colors import AllColors
from math import sqrt, tan, cos

def normalizeAngle(angle: float) -> float:
    angle = angle % (2 * pi)
    if angle <= 0:
        angle = (2 * pi) + angle
    return angle

def distance_between(x1, y1, x2, y2):
    return sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))

class Ray:
    def __init__(self, angle: float, player: Player, mapa: Mapa,
                 colors: tuple[int, int, int, int],
                 colors2: tuple[int, int, int, int]) -> None:
        self.colors1 = colors
        self.colors2 = colors2

        self.rayAngle = normalizeAngle(angle)
        self.player = player
        self.mapa = mapa

        self.is_facing_down = self.rayAngle > 0 and self.rayAngle < pi
        self.is_facing_up = not self.is_facing_down
        self.is_facing_right = self.rayAngle < 0.5 * pi or self.rayAngle > 1.5 * pi
        self.is_facing_left = not self.is_facing_right

        self.wall_hit_x = 0
        self.wall_hit_y = 0 
        self.distance = 0
        self.hit_side = ""
    
    def cast(self) -> None:
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        first_intersection_x = None
        first_intersection_y = None

        cel = self.mapa.setings.CELS_SIZE
        if self.is_facing_up:
            first_intersection_y = ((self.player.y) // cel) * cel - 0.0001
        elif self.is_facing_down:
            first_intersection_y = ((self.player.y // cel) * cel) + cel
        else:
            first_intersection_y = self.player.y

        if tan(self.rayAngle) != 0:
            first_intersection_x = self.player.x + (first_intersection_y - self.player.y) / tan(self.rayAngle)
        else:
            first_intersection_x = self.player.x

        next_horizontal_x = first_intersection_x
        next_horizontal_y = first_intersection_y

        xa = 0
        ya = 0

        if self.is_facing_up:
            ya = -cel
        if self.is_facing_down:
            ya = cel

        if tan(self.rayAngle) != 0:
            xa = ya / tan(self.rayAngle)
        else:
            xa = 0

        width = self.mapa.setings.data.WIDTH * cel
        height = self.mapa.setings.data.HEIGHT * cel
        while (next_horizontal_x < width + cel and next_horizontal_x >= -cel and next_horizontal_y < height + cel
               and next_horizontal_y >= -cel):
            dir_vertical = "S" if self.is_facing_up else "N"
            check_y = next_horizontal_y
            check_x = next_horizontal_x
            if (self.mapa.has_wall_at(check_x, check_y, dir_vertical)):
                found_horizontal_wall = True
                horizontal_hit_x = check_x
                horizontal_hit_y = check_y
                break
            else:
                next_horizontal_x += xa
                next_horizontal_y += ya

        found_vertical_wall = False
        vertical_hit_x = 0
        vertical_hit_y = 0

        horizontal_distance = 0
        vertical_distance = 0

        if self.is_facing_left:
            first_intersection_x = ((self.player.x) // cel) * cel - 0.0001
        elif self.is_facing_right:
            first_intersection_x = ((self.player.x // cel) * cel) + cel
        else:
            first_intersection_x = self.player.x

        first_intersection_y = self.player.y + (first_intersection_x - self.player.x) * tan(self.rayAngle)

        next_vertical_x = first_intersection_x
        next_vertical_y = first_intersection_y

        if self.is_facing_right:
            xa = cel
        if self.is_facing_left:
            xa = -cel

        ya = xa * tan(self.rayAngle)

        while (next_vertical_x < width + cel and next_vertical_x >= -cel and next_vertical_y < height + cel
               and next_vertical_y >= -cel):
            dir_horicont = "E" if self.is_facing_left else "W"
            check_y = next_vertical_y
            check_x = next_vertical_x
            if (self.mapa.has_wall_at(check_x, check_y, dir_horicont)):
                found_vertical_wall = True
                vertical_hit_x = check_x
                vertical_hit_y = check_y
                break
            else:
                next_vertical_x += xa
                next_vertical_y += ya

        if found_horizontal_wall:
            horizontal_distance = distance_between(self.player.x, self.player.y, horizontal_hit_x, horizontal_hit_y)
        else:
            horizontal_distance = 999999
        
        if found_vertical_wall:
            vertical_distance = distance_between(self.player.x, self.player.y, vertical_hit_x, vertical_hit_y)
        else:
            vertical_distance = 999999

        if horizontal_distance < vertical_distance:
            self.wall_hit_x = horizontal_hit_x
            self.wall_hit_y = horizontal_hit_y
            self.distance = horizontal_distance
            self.colors = self.colors2
            self.hit_side = "S" if self.is_facing_up else "N"
        else:
            self.wall_hit_x = vertical_hit_x
            self.wall_hit_y = vertical_hit_y
            self.distance = vertical_distance
            self.colors = self.colors1
            self.hit_side = "E" if self.is_facing_left else "W"

        self.distance *= cos(self.player.rotationAngle - self.rayAngle)      