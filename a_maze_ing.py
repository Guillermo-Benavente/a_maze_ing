#!/usr/bin/env python3
from time import perf_counter
from parser_config import Data, lector
from maze.maze_generator import MazeGenerator
from pydantic import ValidationError
from printer_thing import Drawer
from sys import argv
from maze_3d.player import Player
from maze_3d.map import Map
from maze_3d.data_3d import Data_3D
from maze_3d.raycaster import Raycaster
from colors import ColorCell, AllColors


def _darken(
        c: tuple[int, int, int, int],
        factor: float
) -> tuple[int, int, int, int]:
    """
    Applies a scalar dimension multiplier factor to the RGB components of a
    color tuple.

    Used primarily to bake directional shading and depth shadows into
    the raycasted wall column blocks.

    Args:
        c (tuple[int, int, int, int]): The source RGBA base color tuple.
        factor (float): Shading attenuation scale multiplier (0.0 to 1.0).

    Returns:
        tuple[int, int, int, int]: The shaded destination RGBA color tuple.
    """
    return (int(c[0] * factor), int(c[1] * factor), int(c[2] * factor), c[3])


def __cube3D(data: Data, maze: MazeGenerator) -> None:
    """
    Configures structural tracking instances, sets directional ambient shading
    profiles, and enters the pseudo-3D Raycaster projection camera window loop.

    Args:
        data (Data): Parsed and validated configuration dataset rules.
        maze (MazeGenerator): The source maze grid layout tracking structure.
    """
    setings = Data_3D(data)
    map = Map(maze.maze, setings)
    play = Player(setings, map)
    colors1 = AllColors()
    wall_base = colors1.get_color(ColorCell.WALL.value)
    wall_n = wall_base
    wall_s = _darken(wall_base, 0.7)
    wall_e = _darken(wall_base, 0.85)
    wall_w = _darken(wall_base, 0.55)
    colors3 = colors1.get_color(ColorCell.FLOOR.value)
    floor_entry = colors1.get_color(ColorCell.ENTRY.value)
    floor_exit = colors1.get_color(ColorCell.EXIT.value)
    floor_42 = colors1.get_color(ColorCell.FLOOR_42.value)
    wall_42 = colors1.get_color(ColorCell.WALL_42.value)
    colors1.all_colors()
    ray = Raycaster(play, map, wall_n, wall_s, wall_e, wall_w, colors3,
                    floor_entry, floor_exit, floor_42, wall_42)
    draw = Drawer(maze)
    draw.visualizer_3d(play, ray)


def __printmaze(data: Data | None, maze: MazeGenerator) -> None:
    """
    Launches and manages the interactive 2D top-down grid visualization canvas.

    Enters an execution sequence that allows continuous hot-reloading of new
    maze parameters on demand when configuration files change. It tracks and
    prints the overall runtime efficiency metrics to standard output upon
    final exit.

    Args:
        data (Data | None): Validated initial configuration instance
            parameters.
        maze (MazeGenerator): The generated maze data structure to map on
            screen.
    """
    start_time: float = perf_counter()
    mlx = None
    while data is not None:
        draw = Drawer(maze)
        draw.visualizer(mlx)
        data = draw.new_data
        mlx = draw.mlx
        if data:
            maze = MazeGenerator(data.to_maze_config())
    end_time: float = perf_counter()
    total_time: float = end_time - start_time
    print("\n¡Proceso completado!")
    print(f"Tiempo total: {total_time:.4f} segundos")


if __name__ == "__main__":
    if len(argv[1:]) != 1:
        print("There aren't configuration")
        exit()
    try:
        data = Data.model_validate(lector(argv[1]))
        maze: MazeGenerator = MazeGenerator(data.to_maze_config())
        if data.VISUAL3D:
            __cube3D(data, maze)
        else:
            __printmaze(data, maze)

    except (ValidationError, ValueError, AssertionError, PermissionError) as e:
        if isinstance(e, ValidationError):
            for error in e.errors():
                print(error["msg"])
        else:
            print(e)
    except Exception as e:
        print(e)
