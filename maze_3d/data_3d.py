from parser_config import Data
from math import pi


class Data_3D:
    """
    Configuration wrapper that binds structural maze layout variables
    to specific math, dimension, and resolution settings required by
    the pseudo-3D Raycaster engine.
    """
    data: Data
    CELS_SIZE: int
    WINDOW_WIDTH: int
    WINDOW_HEIGHT: int
    VISION: float
    RESOLUTION: int
    NUM_RAYS: int

    def __init__(self, data: Data):
        """
        Initializes the 3D raycasting camera setting properties, calculating
        the field of view angles and display column count allocations.

        Args:
            data (Data): Parsed and validated primary input configurations
                tracking the dimensions and coordinates of the maze.
        """
        self.data = data
        self.CELS_SIZE = 32
        """
        The spatial pixel dimension used to track standard square matrix grid
        cells.
        """

        self.WINDOW_WIDTH = 800
        """
        Total horizontal pixel window width allocation for the 3D projection
        window.
        """

        self.WINDOW_HEIGHT = 700
        """
        Total vertical pixel window height allocation for the 3D projection
        window.
        """

        self.VISION = 60 * (pi / 180)
        """
        The camera lens horizontal Field of View (FOV) bound, expressed in
        radians.
        """

        self.RESOLUTION = 4
        """
        The pixel thickness step width assigned to each projected vertical
        wall strip column.
        """

        self.NUM_RAYS = self.WINDOW_WIDTH // self.RESOLUTION
        """
        Total number of individual vector rays to project, matching the window
        width columns.
        """
