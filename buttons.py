from enum import Enum


class Buttons(Enum):
    """
    An enumeration mapping human-readable keyboard button constants
    to their corresponding hardware keycode integer definitions
    received from the MiniLibX graphical server backend hooks.
    """
    # Alphabetical Key Codes
    BUTTON_Q = 113
    BUTTON_W = 119
    BUTTON_E = 101
    BUTTON_R = 114
    BUTTON_T = 116
    BUTTON_Y = 121
    BUTTON_U = 117
    BUTTON_I = 105
    BUTTON_O = 111
    BUTTON_P = 112
    BUTTON_A = 97
    BUTTON_S = 115
    BUTTON_D = 100
    BUTTON_F = 102
    BUTTON_G = 103
    BUTTON_H = 104
    BUTTON_J = 106
    BUTTON_K = 107
    BUTTON_L = 108
    BUTTON_Z = 122
    BUTTON_X = 120
    BUTTON_C = 99
    BUTTON_V = 118
    BUTTON_B = 98
    BUTTON_N = 110
    BUTTON_M = 109

    # Numerical Top Row Key Codes
    BUTTON_1 = 49
    BUTTON_2 = 50
    BUTTON_3 = 51
    BUTTON_4 = 52
    BUTTON_5 = 53
    BUTTON_6 = 54
    BUTTON_7 = 55
    BUTTON_8 = 56
    BUTTON_9 = 57
    BUTTON_0 = 48

    # Special Action and Modifier Key Codes
    BUTTON_SIFT = 65505
    BUTTON_SPACE = 32
    BUTTON_SCAPE = 65307
    BUTTON_LEFT_CONTROL = 65507
    BUTTON_RIGHT_CONTROL = 65508
    BUTTON_TAB = 65289

    # Directional Arrow Key Codes
    BUTTON_UP = 65362
    BUTTON_LEFT = 65361
    BUTTON_DOWN = 65364
    BUTTON_RIGHT = 65363

    # Numeric Numpad Key Codes
    BUTTON_NUMPATH_1 = 65436
    BUTTON_NUMPATH_2 = 65433
    BUTTON_NUMPATH_3 = 65435
    BUTTON_NUMPATH_4 = 65430
    BUTTON_NUMPATH_5 = 65437
    BUTTON_NUMPATH_6 = 65432
    BUTTON_NUMPATH_7 = 65429
    BUTTON_NUMPATH_8 = 65431
    BUTTON_NUMPATH_9 = 65434
    BUTTON_NUMPATH_0 = 65438
