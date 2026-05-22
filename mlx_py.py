from typing import Any
from mlx import Mlx


class FlatCanvas:
    BYTES_PER_PIXEL: int = 4
    bytes: Any
    line_size: Any

    def __init__(self, data_addr: tuple[Any, Any]):
        self.bytes, self.line_size = data_addr

    def fill_all(
        self,
        width: int,
        height: int,
        color: tuple[int, int, int, int]
    ) -> None:
        color_row: bytes = bytes(color) * width
        row_bytes_len = width * self.BYTES_PER_PIXEL
        for current_row in range(height):
            start_byte_address = current_row * self.line_size
            self.bytes[start_byte_address : start_byte_address + row_bytes_len] = color_row

    def draw_rectangle(
        self, 
        origin_x: int, 
        origin_y: int, 
        width: int, 
        height: int, 
        color: tuple[int, int, int, int]
    ) -> None:
        color_row: bytes = bytes(color) * width
        row_bytes_len: int = width * self.BYTES_PER_PIXEL
        for current_row in range(height):
            start_byte_address = (
                (origin_y + current_row) * self.line_size
                + origin_x * self.BYTES_PER_PIXEL
            )
            self.bytes[start_byte_address : start_byte_address + row_bytes_len] = color_row

    def draw_horizontal_line(
        self, 
        origin_x: int, 
        origin_y: int, 
        length: int, 
        color: tuple[int, int, int, int]
    ) -> None:
        self.draw_rectangle(origin_x, origin_y, length, 1, color)

    def draw_vertical_line(
        self, 
        origin_x: int, 
        origin_y: int,  
        length: int, 
        color: tuple[int, int, int, int]
    ) -> None:
        color_bytes: bytes = bytes(color)
        for current_row in range(length):
            start_byte_address = (
                (origin_y + current_row) * self.line_size
                + origin_x * self.BYTES_PER_PIXEL
            )
            self.bytes[start_byte_address : start_byte_address + self.BYTES_PER_PIXEL] = color_bytes


class MlxPy:
    mlx: Mlx
    mlx_ptr: Any
    window: Any
    image: Any
    flat_canvas: FlatCanvas


    def __init__(self) -> None:
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.mlx.mlx_ptr = self.mlx_ptr

    def close_window(self) -> None:
        """Destruye la ventana y la imagen actuales para liberar memoria."""
        if hasattr(self, 'image') and self.image:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.image)
            self.image = None
        if hasattr(self, 'window') and self.window:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.window)
            self.window = None

    def new_window(
        self,
        title: str,
        width: int,
        height: int,
        menu_w,
        menu_h,
        margin: int = 0
    ) -> None:
        self.window = self.mlx_new_window(title, width + menu_w, height + menu_h, margin)
        self.image = self.mlx_new_image(width, height)
        self.flat_canvas = self.mlx_get_data_addr()
    
    def load_window(
        self,
        callback: Any,
        menu: Any,
        initial_point: int = 0,
        menu_w: int = 0
    ):
        self.mlx_put_image_to_window(initial_point, menu_w)
        self.mlx_key_hook(callback)
        self.mlx_expose_hook(menu)
        self.mlx_loop()

    def mlx_new_window(
        self,
        title: str,
        window_width: int,
        window_height: int,
        margin: int = 0
    ) -> Any:
        double_margin: int = margin * 2
        return self.mlx.mlx_new_window(
            self.mlx_ptr,
            window_width + double_margin,
            window_height + double_margin,
            title
        )

    def mlx_new_image(
        self,
        image_width,
        image_height
    ) -> Any:
        return self.mlx.mlx_new_image(
            self.mlx_ptr,
            image_width,
            image_height
        )

    def mlx_get_data_addr(self) -> Any:
        [
            bytes, _,
            size_line, _
        ] = self.mlx.mlx_get_data_addr(self.image)
        return FlatCanvas((bytes, size_line))
    
    def mlx_put_image_to_window(self, initial_point: int, menu_w: int = 0) -> None:
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.image,
            menu_w // 2 or 0 + initial_point,
            initial_point
        )

    def mlx_key_hook(self, callback: Any) -> None:
        self.mlx.mlx_key_hook(self.window, callback, self.mlx)

    def mlx_loop(self) -> None:
        self.mlx.mlx_loop(self.mlx_ptr)
    
    def mlx_do_sync(self) -> None:
        self.mlx.mlx_do_sync(self.mlx_ptr)

    def mlx_expose_hook(self, callback: Any) -> None:
        self.mlx.mlx_expose_hook(self.window, callback, self.mlx)
        
    def mlx_string_put(self, x: int, y: int, color: Any, text: str) -> None:
        self.mlx.mlx_string_put(self.mlx_ptr, self.window, x, y, color, text)