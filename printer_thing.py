from ctypes import CDLL, c_void_p
from typing import Callable, Optional

lib = CDLL("./libmlx.so")


def ptint_map(map: list[list[str]], mlx: int,
              funcion: Optional[Callable] = None) -> None:
    ...


if __name__ == "__main__":
    lib.mlx_init.restype = c_void_p
    mlx: c_void_p = lib.mlx_init()
    print("funciona")
    lib.mlx_release.argtypes = [c_void_p]
    lib.mlx_release(mlx)
