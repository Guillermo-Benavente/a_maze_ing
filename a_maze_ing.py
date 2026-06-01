#!/usr/bin/env python3
# from os import path, makedirs
from time import perf_counter, sleep
from parser_config import Data, lector
from maze.maze_generator import MazeGenerator
from pydantic import ValidationError
from printer_thing import Drawer
from sys import argv
from maze_3d.player import Player
from maze_3d.mapa import Mapa
from maze_3d.data_3d import Data_3D
from maze_3d.raycaster import Raycaster
from colors import ColorCell, AllColors


"""if __name__ == "__main__":
    try:
        start_time: float = perf_counter()
        data = Data.model_validate(lector("config.txt"))
        output_folder: str = "mazes_generated"
        if not path.exists(output_folder):
            makedirs(output_folder)
            print("create ")
        for i in range(100):
            data.SEED = i
            maze: Maze = Maze(data)
            filename: str = f"maze_seed_{i}.txt"
            filepath: str = path.join(output_folder, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                maze.view_maze_ascii(f)
        end_time: float = perf_counter()
        total_time: float = end_time - start_time
        print(f"\n¡Proceso completado!")
        print(f"Tiempo total: {total_time:.4f} segundos")
        print(f"Promedio por laberinto: {total_time / 100:.4f} segundos")
    except (ValidationError, ValueError, AssertionError, PermissionError) as e:
        if isinstance(e, ValidationError):
            for error in e.errors():
                print(error["msg"])
        else:
            print(e)"""


def _darken(c: tuple[int, int, int, int], factor: float) -> tuple[int, int, int, int]:
    return (int(c[0] * factor), int(c[1] * factor), int(c[2] * factor), c[3])

def __cube3D(data: Data, maze: MazeGenerator) -> None:
    setings = Data_3D(data)
    mapa = Mapa(maze.maze, setings)
    play = Player(setings, mapa)
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
    ray = Raycaster(play, mapa, wall_n, wall_s, wall_e, wall_w, colors3,
                    floor_entry, floor_exit, floor_42, wall_42)
    maze.view_maze_ascii()
    draw = Drawer(maze)
    draw.visualizer_3d(play, ray)

def __printmaze(data: Data, maze: MazeGenerator) -> None:
    start_time: float = perf_counter()
    mlx = None
    while data is not None:
        draw = Drawer(maze)
        draw.visualizer(mlx)
        data = draw.new_data
        mlx =  draw.mlx
        if data:
            maze = MazeGenerator(data)
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
        maze: MazeGenerator = MazeGenerator(data)
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
