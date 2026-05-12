# Depenencias
python:
	- pydatic
	- numpy

# MLX

Inicialización:

- `void *mlx_init()` → `void *`  (puntero opaco) — inicializa la librería y devuelve el contexto
- `void mlx_release(void *mlx_ptr)` → `void` libera todos los recursos de la librería

Ventanas:

- `void *mlx_new_window(void *mlx_ptr, int width, int height, char *title)` → `void *` (puntero opaco) — crea una ventana con el tamaño y título dados
- `int mlx_clear_window(void *mlx_ptr, void *win_ptr)` → `int` limpia la ventana poniéndola en negro
- `int mlx_pixel_put(void *mlx_ptr, void *win_ptr, int x, int y, int color)` → `int` dibuja un pixel en la posición x,y con el color dado
- `int mlx_destroy_window(void *mlx_ptr, void *win_ptr)` → `int` destruye y cierra la ventana

Imágenes:

- `void *mlx_new_image(void *mlx_ptr, int width, int height)`→ `void *` (puntero opaco) — crea una imagen vacía en memoria
- `char *mlx_get_data_addr(void *img_ptr, int  *bits_per_pixel, int *size_line, int *endian)` → `char *` devuelve acceso directo a los pixels de la imagen como datos, bits_por_pixel, tamaño_linea, formato
- `int mlx_put_image_to_window(void *mlx_ptr, void *win_ptr, void *img_ptr, int x, int y)` → `int`  dibuja una imagen en la ventana en la posición x,y
- `int mlx_destroy_image(void *mlx_ptr, void *img_ptr)` → `int` destruye la imagen y libera su memoria
- `void *mlx_xpm_file_to_image(void *mlx_ptr, char *filename, int *width, int *height)` → `void *` carga un archivo XPM y devuelve img_ptr, width, height
- `void *mlx_png_file_to_image(void *mlx_ptr, char *filename, int *width, int *height)` → `void *` carga un archivo PNG y devuelve img_ptr, width, height

Eventos y loop:

- `int mlx_loop(void *mlx_ptr)` → `int` nicia el loop principal que mantiene la ventana activa y escucha eventos
- `int mlx_loop_exit(void *mlx_ptr)` → `int` termina el loop principal
- `int mlx_key_hook(void *win_ptr, int (*callback)(), void *param)` → `int` registra una función que se llama cuando se suelta una tecla
- `int mlx_mouse_hook(void *win_ptr, int (*callback)(), void *param)` → `int` registra una función que se llama cuando se hace click
- `int mlx_expose_hook(void *win_ptr, int (*callback)(), void *param)` → `int` registra una función que se llama cuando la ventana necesita redibujarse
- `int mlx_loop_hook(void *mlx_ptr, int (*callback)(), void *param)` → `int` registra una función que se llama en cada iteración del loop
- `int mlx_hook(void *win_ptr, int x_event, int x_mask, int (*callback)(), void *param)` → `int` hook genérico para cualquier evento X11

Ratón:

- `int mlx_mouse_hide(void *mlx_ptr)` → `int`  oculta el cursor del ratón
- `int mlx_mouse_show(void *mlx_ptr)` → `int` muestra el cursor del ratón
- `int mlx_mouse_move(void *mlx_ptr, int x, int y)` → `int` mueve el cursor a la posición x,y
- `int mlx_mouse_get_pos(void *mlx_ptr, int *x, int *y)` → `int` devuelve la posición actual del cursor como val, x, y

Misc:

- `int mlx_string_put(void *mlx_ptr, void *win_ptr, int x, int y, int color, char *string)` → `int` escribe texto en la ventana en la posición x,y con el color dado
- `int mlx_get_screen_size(void *mlx_ptr, int *width, int *height)` → `int` devuelve el tamaño de la pantalla como val, width, height
- `int mlx_do_sync(void *mlx_ptr)` → `int` fuerza la sincronización de todos los cambios pendientes en pantalla
- `int mlx_sync(void *mlx_ptr, int cmd, void *img_or_win_ptr)` → `int` sincronización avanzada con control del modo mediante cmd
- `int mlx_do_key_autorepeatoff(void *mlx_ptr)` → `int` desactiva la repetición automática de teclas al mantenerlas pulsadas
- `int mlx_do_key_autorepeaton(void *mlx_ptr)` → `int` activa la repetición automática de teclas al mantenerlas pulsadas