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
    def __init__(self, angle: float, player: Player, mapa: Mapa, colors: tuple[int, int, int, int]) -> None:
        self.colors1 = colors

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
    
    def cast(self) -> None:
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        first_intersection_x = None
        first_intersection_y = None

        cel = self.mapa.setings.CELS_SIZE
        if self.is_facing_up:
            first_intersection_y = ((self.player.y) // cel) * cel - 0.01
        elif self.is_facing_down:
            first_intersection_y = ((self.player.y // cel) * cel) + cel

        first_intersection_x = self.player.x + (first_intersection_y - self.player.y) / tan(self.rayAngle)

        next_horizontal_x = first_intersection_x
        next_horizontal_y = first_intersection_y

        xa = 0
        ya = 0

        if self.is_facing_up:
            ya = -cel
        if self.is_facing_down:
            ya = cel

        xa = ya / tan(self.rayAngle)

        width = self.mapa.setings.WINDOW_WIDTH
        while (next_horizontal_x <= width and next_horizontal_x >= 0 and next_horizontal_y <= width
               and next_horizontal_y >= 0):
            if (self.mapa.has_wall_at(next_horizontal_x, next_horizontal_y, "S")
                or self.mapa.has_wall_at(next_horizontal_x, next_horizontal_y - 1, "N")):
                found_horizontal_wall = True
                horizontal_hit_x = next_horizontal_x
                horizontal_hit_y = next_horizontal_y
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
            first_intersection_y = ((self.player.y) // cel) * cel - 0.01
        elif self.is_facing_right:
            first_intersection_y = ((self.player.y // cel) * cel) + cel
        first_intersection_y = self.player.y + (first_intersection_x - self.player.x) * tan(self.rayAngle)

        next_vertical_x = first_intersection_x
        next_vertical_y = first_intersection_y

        if self.is_facing_right:
            xa = cel
        if self.is_facing_left:
            xa = -cel

        ya = xa * tan(self.rayAngle)

        while (next_vertical_x <= width and next_vertical_x >= 0 and next_vertical_y <= width
               and next_vertical_y >= 0):
            if (self.mapa.has_wall_at(next_vertical_x - 1, next_vertical_y, "E")
                or self.mapa.has_wall_at(next_vertical_x, next_vertical_y, "W")):
                found_vertical_wall = True
                vertical_hit_x = next_vertical_x
                vertical_hit_y = next_vertical_y
                break
            else:
                next_vertical_x += xa
                next_vertical_y += ya

        if found_horizontal_wall:
            horizontal_distance = distance_between(self.player.x, self.player.y, horizontal_hit_x, horizontal_hit_y)
        else:
            horizontal_distance = 9999
        
        if found_vertical_wall:
            vertical_distance = distance_between(self.player.x, self.player.y, vertical_hit_x, vertical_hit_y)
        else:
            vertical_distance = 9999

        if horizontal_distance < vertical_distance:
            self.wall_hit_x = horizontal_hit_x
            self.wall_hit_y = horizontal_hit_y
            self.distance = horizontal_distance
            self.colors = tuple(i - 0xA0 if i - 0xA0 > 0 else 0 for i in self.colors1)
            self.colors = tuple((self.colors[0], self.colors[1], self.colors[2], 0xFF))
        else:
            self.wall_hit_x = vertical_hit_x
            self.wall_hit_y = vertical_hit_y
            self.distance = vertical_distance
            self.colors = self.colors1

            self.distance *= cos(self.player.rotationAngle - self.rayAngle)      