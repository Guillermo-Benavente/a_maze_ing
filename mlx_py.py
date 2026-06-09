from typing import Any, Set
from mlx import Mlx  # type: ignore[import-untyped, unused-ignore]


class FlatCanvas:
    """
    Represents a two-dimensional drawing canvas operating directly on the
    MiniLibX image pixel data buffer via raw memory modifications.
    """
    BYTES_PER_PIXEL: int = 4
    bytes: Any
    line_size: Any

    def __init__(self, data_addr: tuple[Any, Any]):
        """
        Initializes the flat canvas by binding it to the physical image
        buffer address and storing the length of a single horizontal
        line in bytes.

        Args:
            data_addr (tuple[Any, Any]): A tuple containing the
                reference/pointer to the image data bytes and the
                line size integer.
        """
        self.bytes, self.line_size = data_addr

    def fill_all(
        self,
        width: int,
        height: int,
        color: tuple[int, int, int, int]
    ) -> None:
        """
        Fills the entire canvas buffer uniformly with a single structured color
        using optimized byte-row assignments.

        Args:
            width (int): The total pixel width of the canvas region.
            height (int): The total pixel height of the canvas region.
            color (tuple[int, int, int, int]): The targeted color defined
                as an RGBA tuple.
        """
        color_row: bytes = bytes(color) * width
        row_bytes_len = width * self.BYTES_PER_PIXEL
        for current_row in range(height):
            start_byte_address = current_row * self.line_size
            self.bytes[
                start_byte_address: start_byte_address + row_bytes_len
            ] = color_row

    def draw_rectangle(
        self,
        origin_x: int,
        origin_y: int,
        width: int,
        height: int,
        color: tuple[int, int, int, int]
    ) -> None:
        """
        Draws a solid filled rectangle into a localized matrix coordinate of
        the canvas while validating buffer boundary safety limits to avoid
        memory faults.

        Args:
            origin_x (int): The top-left horizontal coordinate (X) in pixels.
            origin_y (int): The top-left vertical coordinate (Y) in pixels.
            width (int): The horizontal width of the rectangle in pixels.
            height (int): The vertical height of the rectangle in pixels.
            color (tuple[int, int, int, int]): The structural color defined
                as an RGBA tuple.
        """
        color_row: bytes = bytes(color) * width
        row_bytes_len: int = width * self.BYTES_PER_PIXEL
        for current_row in range(height):
            start_byte_address = (
                (origin_y + current_row) * self.line_size
                + origin_x * self.BYTES_PER_PIXEL
            )
            if (start_byte_address >= 0 and
               start_byte_address + row_bytes_len <= len(self.bytes)):
                self.bytes[
                    start_byte_address: start_byte_address + row_bytes_len
                ] = color_row

    def draw_horizontal_line(
        self,
        origin_x: int,
        origin_y: int,
        length: int,
        color: tuple[int, int, int, int]
    ) -> None:
        """
        Draws a one-pixel high horizontal line by reusing the rectangle
        drawing operation.

        Args:
            origin_x (int): Starting horizontal index coordinate.
            origin_y (int): Starting vertical index coordinate.
            length (int): Total horizontal span length in pixels.
            color (tuple[int, int, int, int]): Color data defined as an
                RGBA tuple.
        """
        self.draw_rectangle(origin_x, origin_y, length, 1, color)

    def draw_vertical_line(
        self,
        origin_x: int,
        origin_y: int,
        length: int,
        color: tuple[int, int, int, int]
    ) -> None:
        """
        Draws a one-pixel wide vertical line by looping iteratively down the
        buffer rows and updating individual pixel memory locations.

        Args:
            origin_x (int): Starting horizontal index coordinate.
            origin_y (int): Starting vertical index coordinate.
            length (int): Total vertical span length down the matrix in pixels.
            color (tuple[int, int, int, int]): Color data defined as an RGBA
                tuple.
        """
        color_bytes: bytes = bytes(color)
        for current_row in range(length):
            start_byte_address = (
                (origin_y + current_row) * self.line_size
                + origin_x * self.BYTES_PER_PIXEL
            )
            self.bytes[
                start_byte_address: start_byte_address + self.BYTES_PER_PIXEL
            ] = color_bytes


class MlxPy:
    """
    An interface wrapper encapsulating the core MiniLibX subsystems.
    Manages display environments, graphics instances, memory cleanup,
    and input hooks.
    """
    mlx: Mlx
    mlx_ptr: Any
    window: Any
    image: Any
    flat_canvas: FlatCanvas

    def __init__(self) -> None:
        """
        Instantiates the MiniLibX connection handler, initializes tracking
        structures for user keyboard inputs, and triggers display subsystem
        creation.
        """
        self.mlx = Mlx()
        self.pressed_keys: Set[int] = set()
        self.__create_display()

    def __create_display(self) -> None:
        """
        Private method establishing the underlying connection to the screen
        server by initializing the core system graphics pointers.
        """
        self.mlx_ptr = self.mlx.mlx_init()
        self.mlx.mlx_ptr = self.mlx_ptr

    def close_window(self) -> None:
        """
        Destroys and releases currently allocated image assets and window
        contexts from the screen server safely to prevent system memory leaks.
        """
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
        menu_w: int,
        menu_h: int,
        margin: int = 0
    ) -> None:
        """
        Generates a new window taking into account interface menu offsets and
        safety margins, initializes the render target canvas buffer,
        and attaches the memory instance wrapper.

        Args:
            title (str): Text string displayed in the application title bar.
            width (int): Target interactive width of the maze render region.
            height (int): Target interactive height of the maze render region.
            menu_w (int): Extra width buffer allocated for UI menus.
            menu_h (int): Extra height buffer allocated for UI menus.
            margin (int, optional): Extra padding margin applied around the
                screen context. Defaults to 0.
        """
        self.window = self.mlx_new_window(
            title, width + menu_w,
            height + menu_h,
            margin
        )
        self.image = self.mlx_new_image(width, height)
        self.flat_canvas = self.mlx_get_data_addr()

    def load_window(
        self,
        callback: Any,
        menu: Any,
        initial_point: int = 0,
        menu_w: int = 0
    ) -> None:
        """
        Pushes structural canvas updates onto the window instance,
        binds menu rendering events, synchronizes graphical
        buffers, registers key inputs,and boots the infinite
        event loop.

        Args:
            callback (Any): Execution function routinely processing key inputs
                or logic ticks.
            menu (Any): Call routine handling interface menus or background
                layouts drawing hooks.
            initial_point (int, optional): Initial horizontal offset position.
                Defaults to 0.
            menu_w (int, optional): Width sizing specification of the graphical
                menu. Defaults to 0.
        """
        self.mlx_put_image_to_window(initial_point, menu_w)
        self.mlx_expose_hook(menu)
        self.mlx_do_sync()
        self.mlx_key_hook(callback)
        self.mlx_loop()

    def mlx_new_window(
        self,
        title: str,
        window_width: int,
        window_height: int,
        margin: int = 0
    ) -> Any:
        """
        Creates and returns a raw system window pointer configured with
        absolute sizes.

        Args:
            title (str): Title header display name for the new window.
            window_width (int): Core horizontal content sizing requested.
            window_height (int): Core vertical content sizing requested.
            margin (int, optional): Safety frame pixel spacing size.
                Defaults to 0.

        Returns:
            Any: A raw pointer targeting the instantiated window structure.
        """
        double_margin: int = margin * 2
        return self.mlx.mlx_new_window(
            self.mlx_ptr,
            window_width + double_margin,
            window_height + double_margin,
            title
        )

    def mlx_new_image(
        self,
        image_width: int,
        image_height: int
    ) -> Any:
        """
        Creates an internal backend memory raster image buffer of specified
        dimensions.

        Args:
            image_width (int): Image layout resolution width.
            image_height (int): Image layout resolution height.

        Returns:
            Any: Punter reference pointing to the new memory-backed image
                structure.
        """
        return self.mlx.mlx_new_image(
            self.mlx_ptr,
            image_width,
            image_height
        )

    def mlx_get_data_addr(self) -> Any:
        """
        Queries and retrieves raw memory structural address definitions from
        the image object, instantiating and returning a usable FlatCanvas
        tracker.

        Returns:
            Any: A FlatCanvas object initialized with raw byte buffer
                properties.
        """
        [
            bytes, _,
            size_line, _
        ] = self.mlx.mlx_get_data_addr(self.image)
        return FlatCanvas((bytes, size_line))

    def mlx_put_image_to_window(
            self,
            initial_point: int,
            menu_w: int = 0
    ) -> None:
        """
        Pushes and renders the internally managed image pixel buffer onto the
        window view offsetting coordinates to fit interface requirements.

        Args:
            initial_point (int): Base drawing displacement coordinate tracker.
            menu_w (int, optional): Width allocated for menus to adjust
                rendering origins. Defaults to 0.
        """
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.window,
            self.image,
            menu_w // 2 or 0 + initial_point,
            initial_point
        )

    def mlx_key_hook(self, callback: Any) -> None:
        """
        Registers a high-level keyboard handler callback function directly
        within MiniLibX.

        Args:
            callback (Any): The function triggered upon standard key events.
        """
        self.mlx.mlx_key_hook(self.window, callback, self.mlx)

    def mlx_loop(self) -> None:
        """
        Starts the blocking infinite execution loop of MiniLibX to track
        system events.
        """
        self.mlx.mlx_loop(self.mlx_ptr)

    def mlx_do_sync(self) -> None:
        """
        Flushes and forces immediate frame buffer updates onto the screen to
        prevent anomalies.
        """
        self.mlx.mlx_do_sync(self.mlx_ptr)

    def mlx_expose_hook(self, callback: Any) -> None:
        """
        Attaches an expose handler routine called whenever the window
        gets uncovered or redrawn.

        Args:
            callback (Any): Redraw routine invoked on window visibility
                adjustments.
        """
        self.mlx.mlx_expose_hook(self.window, callback, self.mlx)

    def mlx_string_put(self, x: int, y: int, color: Any, text: str) -> None:
        """
        Renders a raw text string onto the window utilizing MiniLibX font
        configurations.

        Args:
            x (int): Horizontal placement coordinate in pixels.
            y (int): Vertical placement coordinate in pixels.
            color (Any): Numerical or hexadecimal color parameter used to
                style the text.
            text (str): String message contents to write down.
        """
        self.mlx.mlx_string_put(self.mlx_ptr, self.window, x, y, color, text)

    def mlx_loop_exit(self) -> None:
        """
        Triggers a clean loop disruption to interrupt execution cycles safely.
        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def load_window_3d(
        self,
        callback: Any,
        initial_point: int = 0
    ) -> None:
        """
        Initializes rendering processes for 3D engine instances,
        registers hardware input triggers, and enters the event
        processing loop.

        Args:
            callback (Any): Core frames processing routine called
                continuously by the loop hook.
            initial_point (int, optional): Initial drawing coordinate
                offset parameter. Defaults to 0.
        """
        self.mlx_put_image_to_window(initial_point)
        self.mlx_do_sync()
        self.setup_input_hooks(callback)
        self.mlx_loop()

    def setup_input_hooks(self, loop_callback: Any) -> None:
        """
        Wires fundamental hardware loop listeners tracking button
        modifications and hooks upthe application main drawing
        cycles.

        Args:
            loop_callback (Any): Target framework tick routine
                processing iterative calculations.
        """
        self.mlx.mlx_hook(self.window, 2, 1, self.__key_press, None)

        self.mlx.mlx_hook(self.window, 3, 2, self.__key_release, None)

        self.mlx.mlx_loop_hook(self.mlx_ptr, loop_callback, self.mlx)

    def __key_press(self, keycode: int, param: Any) -> None:
        """
        Inserts a targeted hardware key value into the tracked tracking set
        structure.

        Args:
            keycode (int): Integer identifier specifying the pressed key.
            param (Any): Context data block reference passed down natively
                by MiniLibX hooks.
        """
        self.pressed_keys.add(keycode)

    def __key_release(self, keycode: int, param: Any) -> None:
        """
        Discards a targeted hardware key value from the active tracking set
        structure.

        Args:
            keycode (int): Integer identifier specifying the released key.
            param (Any): Context data block reference passed down natively by
                MiniLibX hooks.
        """
        self.pressed_keys.discard(keycode)

    def key_pressed(self) -> list[int]:
        """
        Extracts a snapshot list containing every keycode currently
        held down by the user.

        Returns:
            list[int]: A clean numerical list containing the currently
                pressed key values.
        """
        return list(self.pressed_keys)
