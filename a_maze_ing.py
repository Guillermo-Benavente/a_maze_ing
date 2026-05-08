#!/usr/bin/env python3
from parser_config import Data, lector
from maze.maze import Maze
from pydantic import ValidationError


if __name__ == "__main__":
    try:
        data = Data.model_validate(lector("config.txt"))
        maze = Maze(data)
        maze.view_maze_ascii()
        maze.view_maze()
    except (ValidationError, ValueError, AssertionError, PermissionError) as e:
        if isinstance(e, ValidationError):
            for error in e.errors():
                print(error["msg"])
        else:
            print(e)
