from mlx import Mlx

CELL_SIZE = 40

hola = """9515391539551795151151153
EBABAE812853C1412BA812812
96A8416A84545412AC4282C2A
C3A83816A9395384453A82D02
96842A852AC07AAD13A8283C2
C1296C43AAB83AA92AA8686BA
92E853968428444682AC12902
AC3814452FA83FFF82C52C42A
85684117AFC6857FAC1383D06
C53AD043AFFFAFFF856AA8143
91441294297FAFD501142C6BA
AA912AC3843FAFFF82856D52A
842A8692A92B8517C4451552A
816AC384468285293917A9542
C416928513C443A828456C3BA
91416AA92C393A82801553AAA
A81292AA814682C6A8693C6AA
A8442C6C2C1168552C16A9542
86956951692C1455416928552
C545545456C54555545444556"""

mapa = [list(i) for i in hola.split("\n")]
dic = {c: int(c, 16) for c in "0123456789ABCDEF"}

ROWS = len(mapa)
COLS = len(mapa[0])
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

WALL_COLOR = 0xFFFFFF   # blanco
FLOOR_COLOR = 0x000000  # negro

def draw_maze(m: Mlx, mlx_ptr, data, size_line):
    for y in range(ROWS):
        for x in range(COLS):
            v = dic[mapa[y][x]]
            px = x * CELL_SIZE
            py = y * CELL_SIZE

            # rellenar celda de negro
            for dy in range(CELL_SIZE):
                for dx in range(CELL_SIZE):
                    idx = (py + dy) * size_line + (px + dx) * 4
                    data[idx] = 0x00
                    data[idx + 1] = 0x00
                    data[idx + 2] = 0x00
                    data[idx + 3] = 0xFF

            # pared norte (bit 0)
            if (v >> 0) & 1:
                for dx in range(CELL_SIZE):
                    idx = py * size_line + (px + dx) * 4
                    data[idx] = 0xFF
                    data[idx + 1] = 0xFF
                    data[idx + 2] = 0xFF

            # pared este (bit 1)
            if (v >> 1) & 1:
                for dy in range(CELL_SIZE):
                    idx = (py + dy) * size_line + (px + CELL_SIZE - 1) * 4
                    data[idx] = 0xFF
                    data[idx + 1] = 0xFF
                    data[idx + 2] = 0xFF
                    data[idx + 3] = 0xFF

            # pared sur (bit 2)
            if (v >> 2) & 1:
                for dx in range(CELL_SIZE):
                    idx = (py + CELL_SIZE - 1) * size_line + (px + dx) * 4
                    data[idx] = 0xFF
                    data[idx + 1] = 0xFF
                    data[idx + 2] = 0xFF
                    data[idx + 3] = 0xFF

            # pared oeste (bit 3)
            if (v >> 3) & 1:
                for dy in range(CELL_SIZE):
                    idx = (py + dy) * size_line + px * 4
                    data[idx] = 0xFF
                    data[idx + 1] = 0xFF
                    data[idx + 2] = 0xFF
                    data[idx + 3] = 0xFF


def key_how(key: int, param: Mlx, x = -5, y = -5) -> None:
    if x != -5:
        ... # print(y())
    print(f"{x}, {y}", end=" ")
    print(key)
    if key == 65307:
        param.mlx_loop_exit(param.mlx_ptr)

if __name__ == "__main__":
    m = Mlx()
    m.mlx_ptr = m.mlx_init()
    win = m.mlx_new_window(m.mlx_ptr, WIDTH + 20, HEIGHT + 20, "Laberinto")
    img = m.mlx_new_image(m.mlx_ptr, WIDTH, HEIGHT)

    data, _, size_line, _ = m.mlx_get_data_addr(img)

    draw_maze(m, m.mlx_ptr, data, size_line)

    m.mlx_put_image_to_window(m.mlx_ptr, win, img, 10, 10)
    m.mlx_mouse_hook(win, key_how, m)
    m.mlx_key_hook(win, key_how, m)
    m.mlx_loop(m.mlx_ptr)
