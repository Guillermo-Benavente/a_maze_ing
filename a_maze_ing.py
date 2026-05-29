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
from maze_3d.datas import Datas
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


def __cube3D(data: Data, maze: MazeGenerator) -> None:
    setings = Datas(data)
    play = Player(setings)
    mapa = Mapa(maze.maze, setings)
    colors1 = AllColors()
    colors = colors1.get_color(ColorCell.WALL.value)
    colors3 = colors1.get_color(ColorCell.FLOOR.value)
    colors1.all_colors()
    colors2 = colors1.get_color(ColorCell.WALL.value)
    ray = Raycaster(play, mapa, colors, colors2, colors3)
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
