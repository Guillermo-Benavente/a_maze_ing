from mapa import Mapa
from player import Player, pi
from colors import AllColors
from math import sqrt, tan, cos

def normalizeAngle(angle: float) -> float:
    angle = angle % (2 * pi)
    if angle <= 0:
        angle = (2 * pi)  + angle
    return angle

def distance_between(x1, y1, x2, y2):
    return sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))

class Ray:
    def __init__(self, angle: float, player: Player, map: Mapa, colors: AllColors) -> None:
        self.colors = colors

        self.rayAngle = normalizeAngle(angle)
        self.player = player
        self.map = map

        self.is_facing_down = self.rayAngle > 0 and self.rayAngle < pi
        self.is_facing_up = not self.is_facing_down
        self.is_facing_right = self.rayAngle < 0.5 * pi or self.rayAngle > 1.5 * pi
        self.is_facing_left = not self.is_facing_right

        self.wall_hit_x = 0
        self.wall_hit_y = 0 
        self.distance = 0
    
def cast(self) -> None:
    ...