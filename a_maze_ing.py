#!/usr/bin/env python3
from os import path, makedirs
from time import perf_counter
from parser_config import Data, lector
from maze.maze import Maze
from pydantic import ValidationError
from printer_thing import Drawer
from algoritm import found_all


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


if __name__ == "__main__":
    try:
        start_time: float = perf_counter()
        data = Data.model_validate(lector("config.txt"))
        maze: Maze = Maze(data)
        draw = Drawer(maze)
        end_time: float = perf_counter()
        total_time: float = end_time - start_time
        print(f"\n¡Proceso completado!")
        print(f"Tiempo total: {total_time:.4f} segundos")
        print(f"Promedio por laberinto: {total_time / 100:.4f} segundos")
        funtion = found_all(data.ENTRY, data.EXIT, maze.maze)
        try:
            for i in funtion["algoritm"]():
                ...
        except Exception as e:
            print(e)
        print(funtion["list"]())
        draw.visualizer()
    except (ValidationError, ValueError, AssertionError, PermissionError) as e:
        if isinstance(e, ValidationError):
            for error in e.errors():
                print(error["msg"])
        else:
            print(e)
